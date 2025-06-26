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

logger = logging.getLogger(__name__)

logger.setLevel(Config.LOG_LEVEL)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(LoggingFormatter())
logger.addHandler(handler)


async def main():
    """Main function to run the scraper."""
    logger.info("Starting web scraper...")
    logger.info(f"Target URL: {Config.TARGET_URL}")
    logger.info(f"Target text: {Config.TARGET_TEXT}")
    logger.info(f"Check interval: {Config.CHECK_INTERVAL} seconds")

    scraper = WebScraper(timeout=Config.REQUEST_TIMEOUT, delay=Config.REQUEST_DELAY)
    notifier = Notifier()

    try:
        while True:
            logger.info(f"Checking {Config.TARGET_URL} for '{Config.TARGET_TEXT}'...")

            found = await scraper.check_for_text(Config.TARGET_URL, Config.TARGET_TEXT)

            if found:
                logger.info("Target text found!")
                await notifier.send_notification(f"Text '{Config.TARGET_TEXT}' found on {Config.TARGET_URL}")
            else:
                logger.info("Target text not found.")

            logger.info(f"Waiting {Config.CHECK_INTERVAL} seconds before next check...")
            await asyncio.sleep(Config.CHECK_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Scraper stopped by user.")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        await notifier.send_notification(f"Scraper error: {e}")
    finally:
        await scraper.close()


def run():
    """Entry point for console script."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
