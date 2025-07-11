"""
Web scraper module for extracting content from web pages.
"""

import asyncio
import json
import logging
from typing import Any

import aiohttp
import backoff
from bs4 import BeautifulSoup
from jsonpath_ng.ext import parse as jsonpath_parse

from scrape_and_notify.notifier import Notifier

logger = logging.getLogger(__name__)

_RETRYABLES = (aiohttp.ClientResponseError, aiohttp.ClientError, asyncio.TimeoutError)


class WebScraper:
    """Web scraper for checking if specific text exists on a webpage."""

    def __init__(self, notifier: Notifier, timeout: int = 30, delay: float = 1.0):
        """
        Initialize the web scraper.

        Args:
            timeout: Request timeout in seconds
            delay: Delay between requests to be respectful
            notifier: Notifier instance for sending error notifications
        """
        self.notifier = notifier
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.delay = delay
        self.session: aiohttp.ClientSession | None = None

        # Headers to avoid being blocked
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout, headers=self.headers)
        return self.session

    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()

    @backoff.on_exception(backoff.expo, _RETRYABLES, max_tries=5)
    async def _fetch_page_with_retries(self, url: str) -> str:
        session = await self._get_session()
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    
    async def fetch_page(self, url: str) -> str | None:
        """
        Fetch the content of a web page.

        Args:
            url: The URL to fetch

        Returns:
            The page content as a string, or None if failed
        """
        try:
            logger.debug(f"Fetching page: {url}")
            await asyncio.sleep(self.delay)  # Be respectful

            return await self._fetch_page_with_retries(url)

        except aiohttp.ClientResponseError as e:
            # Handle HTTP status errors from response.raise_for_status()
            logger.exception(f"HTTP error {e.status} occurred while fetching {url}: {e.message}")
            await self.notifier.send_notification(f"HTTP {e.status} error occurred while checking {url}: {e.message}")
        except aiohttp.ClientError as e:
            logger.exception(f"Error fetching {url}: {e}")
            await self.notifier.send_notification(f"Network error occurred while checking {url}: {str(e)}")
        except asyncio.TimeoutError as e:
            logger.exception(f"Timeout fetching {url}: {e}")
            await self.notifier.send_notification(f"Timeout error occurred while checking {url}: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error fetching {url}: {e}")
            await self.notifier.send_notification(f"Unexpected error occurred while checking {url}: {str(e)}")
        return None

    def parse_content(self, html: str) -> str:
        """
        Parse HTML content and extract text.

        Args:
            html: Raw HTML content

        Returns:
            Cleaned text content
        """
        try:
            soup = BeautifulSoup(html, "lxml")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            return text

        except Exception as e:
            logger.exception(f"Error parsing HTML: {e}")
            return ""

    def parse_json(self, content: str) -> dict | None:
        """
        Parse JSON content.

        Args:
            content: Raw JSON content

        Returns:
            Parsed JSON data or None if parsing fails
        """
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.exception(f"Error parsing JSON: {e}")
            return None

    def check_json_path(self, data: dict, json_path: str, target_value: Any, case_sensitive: bool = False) -> bool:
        """
        Check if a JSON path matches a target value.

        Args:
            data: The JSON data to search
            json_path: JSONPath expression (e.g., "$.my.path")
            target_value: The value to match against
            case_sensitive: Whether the comparison should be case sensitive

        Returns:
            True if the path exists and matches the target value
        """
        try:
            # Parse the JSONPath expression
            jsonpath_expr = jsonpath_parse(json_path)
            matches = [match.value for match in jsonpath_expr.find(data)]

            if not matches:
                logger.debug(f"JSONPath '{json_path}' found no matches")
                return False

            # Check if any match equals the target value
            for match in matches:
                if not case_sensitive:
                    match_str = str(match).lower()
                    target_str = str(target_value).lower()
                else:
                    match_str = str(match)
                    target_str = str(target_value)

                if match_str == target_str:
                    logger.debug(f"JSONPath '{json_path}' found matching value: {match}")
                    return True

            logger.debug(f"JSONPath '{json_path}' found values {matches} but none matched '{target_value}'")
            return False

        except Exception as e:
            logger.exception(f"Error evaluating JSONPath '{json_path}': {e}")
            return False

    async def check_for_text(self, url: str, target_text: str, case_sensitive: bool = False) -> bool:
        """
        Check if specific text exists on a webpage.

        Args:
            url: The URL to check
            target_text: The text to search for
            case_sensitive: Whether the search should be case sensitive

        Returns:
            True if text is found, False otherwise
        """
        html = await self.fetch_page(url)
        if not html:
            return False

        with open("html.html", "w") as f:
            f.write(html)

        content = self.parse_content(html)
        if not content:
            return False
        if not case_sensitive:
            content = content.lower()
            target_text = target_text.lower()

        found = target_text in content
        logger.debug(f"Text '{target_text}' {'found' if found else 'not found'} on {url}")

        return found

    async def check_for_json_match(
        self, url: str, json_path: str, target_value: Any, case_sensitive: bool = False
    ) -> bool:
        """
        Check if a JSON path matches a target value on a webpage that returns JSON.

        Args:
            url: The URL to check (should return JSON)
            json_path: JSONPath expression to evaluate
            target_value: The value to match against
            case_sensitive: Whether the comparison should be case sensitive

        Returns:
            True if the JSON path matches the target value
        """
        content = await self.fetch_page(url)
        if not content:
            return False

        json_data = self.parse_json(content)
        if json_data is None:
            return False

        return self.check_json_path(json_data, json_path, target_value, case_sensitive)

    async def check_content(
        self, url: str, search_type: str, target_match: str, json_path: str | None = None, case_sensitive: bool = False
    ) -> bool:
        """
        Check content based on search type.

        Args:
            url: The URL to check
            search_type: Type of search ('html' or 'json')
            target_match: The value to match against
            json_path: JSONPath expression for JSON searches
            case_sensitive: Whether the search should be case sensitive

        Returns:
            True if the match is found according to the search type
        """
        if search_type.lower() == "json":
            if json_path is None:
                logger.error("JSON search requires a json_path parameter")
                return False
            return await self.check_for_json_match(url, json_path, target_match, case_sensitive)
        elif search_type.lower() == "html":
            return await self.check_for_text(url, target_match, case_sensitive)
        else:
            logger.error(f"Unsupported search type: {search_type}")
            return False

    async def check_for_element(self, url: str, selector: str) -> bool:
        """
        Check if a specific CSS selector exists on a webpage.

        Args:
            url: The URL to check
            selector: CSS selector to search for

        Returns:
            True if element is found, False otherwise
        """
        html = await self.fetch_page(url)
        if not html:
            return False

        try:
            soup = BeautifulSoup(html, "lxml")
            element = soup.select_one(selector)
            found = element is not None

            logger.debug(f"Element '{selector}' {'found' if found else 'not found'} on {url}")
            return found

        except Exception as e:
            logger.exception(f"Error checking for element {selector}: {e}")
            return False
