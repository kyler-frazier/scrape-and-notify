"""
Web scraper module for extracting content from web pages.
"""

import asyncio
import logging
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebScraper:
    """Web scraper for checking if specific text exists on a webpage."""

    def __init__(self, timeout: int = 30, delay: float = 1.0):
        """
        Initialize the web scraper.

        Args:
            timeout: Request timeout in seconds
            delay: Delay between requests to be respectful
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.delay = delay
        self.session: Optional[aiohttp.ClientSession] = None

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

    async def fetch_page(self, url: str) -> Optional[str]:
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

            session = await self._get_session()
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()

        except aiohttp.ClientError as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
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
            logger.error(f"Error parsing HTML: {e}")
            return ""

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
            logger.error(f"Error checking for element {selector}: {e}")
            return False
