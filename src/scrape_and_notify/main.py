"""
Main entry point for the web scraper and notification system.
"""

import asyncio
import logging
import sys

from scrape_and_notify.config import Config
from scrape_and_notify.logging_formatter import LoggingFormatter
from scrape_and_notify.notifier import Notifier
from scrape_and_notify.scraper import RETRYABLE_EXCEPTIONS, WebScraper

logger = logging.getLogger(__name__)


async def main():
    """Main function to run the scraper."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(LoggingFormatter())
    root_logger.addHandler(handler)

    config = Config()
    root_logger.setLevel(config.log_level_int)

    startup_messages = [
        "Starting Scrape and Notify application...",
        f"Target URL: {config.target_url}",
        f"Negative search: {config.negative}",
        f"Search type: {config.search_type}",
        f"Target match: {config.target_match}",
        f"JSON path: {config.target_location}",
        f"Check interval: {config.check_interval} seconds",
    ]
    for message in startup_messages:
        logger.info(message)

    notifier = Notifier(bot_token=config.discord_bot_token, channel_id=config.discord_channel_id)
    scraper = WebScraper(notifier=notifier, timeout=config.request_timeout, delay=config.request_delay)

    await notifier.send_notification("\n".join(startup_messages))

    try:
        while True:
            logger.info(
                f"Checking {config.target_url} for '{config.target_match}' using {config.search_type} search..."
            )

            try:
                found = await scraper.check_content(
                    url=config.target_url,
                    search_type=config.search_type,
                    target_match=config.target_match,
                    json_path=config.target_location,
                )

                search_desc = f"{config.search_type} search for '{config.target_match}' at path '{config.target_location}'"
                if config.negative:
                    search_desc = "Negative " + search_desc
                    found = not found

                if found:
                    logger.info("Target match found!")
                    await notifier.send_notification(f"{search_desc} found on {config.target_url}")
                else:
                    logger.info("Target match not found.")
            except RETRYABLE_EXCEPTIONS:
                logger.exception(f"Failed retryables during scrape...")

            logger.info(f"Waiting {config.check_interval} seconds before next check...")
            await asyncio.sleep(config.check_interval)

    except KeyboardInterrupt:
        logger.info("Scraper stopped by user.")
    except Exception as e:
        logger.exception(f"Error occurred: {e}")
        await notifier.send_notification(f"Scraper error: {e}")
    finally:
        await scraper.close()
        await notifier.close()


def run():
    """Entry point for console script."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
