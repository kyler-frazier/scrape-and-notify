"""
Main entry point for the web scraper and notification system.
"""

import asyncio
import logging
import sys

from scrape_and_notify.config import Config
from scrape_and_notify.logging_formatter import LoggingFormatter
from scrape_and_notify.notifier import Notifier
from scrape_and_notify.scraper import WebScraper

# Instantiate the config
config = Config()

logger = logging.getLogger(__name__)

logger.setLevel(config.log_level_int)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(LoggingFormatter())
logger.addHandler(handler)


async def main():
    """Main function to run the scraper."""
    logger.info("Starting web scraper...")
    logger.info(f"Target URL: {config.target_url}")
    logger.info(f"Search type: {config.search_type}")
    logger.info(f"Target match: {config.target_match}")
    logger.info(f"JSON path: {config.target_location}")
    logger.info(f"Check interval: {config.check_interval} seconds")

    notifier = Notifier(bot_token=config.discord_bot_token, channel_id=config.discord_channel_id)
    scraper = WebScraper(notifier=notifier, timeout=config.request_timeout, delay=config.request_delay)

    try:
        while True:
            logger.info(
                f"Checking {config.target_url} for '{config.target_match}' using {config.search_type} search..."
            )

            found = await scraper.check_content(
                url=config.target_url,
                search_type=config.search_type,
                target_match=config.target_match,
                json_path=config.target_location,
            )

            if found:
                logger.info("Target match found!")
                search_desc = (
                    f"{config.search_type} search for '{config.target_match}' at path '{config.target_location}'"
                )
                await notifier.send_notification(f"{search_desc} found on {config.target_url}")
            else:
                logger.info("Target match not found.")

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
