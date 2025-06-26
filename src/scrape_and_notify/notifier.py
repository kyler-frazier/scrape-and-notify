"""
Notification module for sending alerts via Discord bot when target content is found.
"""

import logging
import os
from datetime import datetime

import discord

logger = logging.getLogger(__name__)


class Notifier:
    """Handle Discord bot notifications."""

    def __init__(self):
        """Initialize the Discord notifier."""
        # Discord configuration (set via environment variables)
        self.bot_token = os.getenv("DISCORD_BOT_TOKEN")
        self.channel_id = os.getenv("DISCORD_CHANNEL_ID")

        if self.channel_id:
            self.channel_id = int(self.channel_id)

        # Initialize Discord client
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)

    async def send_notification(self, message: str, title: str = "Scraper Alert") -> bool:
        """
        Send notification via Discord bot.

        Args:
            message: The notification message
            title: The notification title

        Returns:
            True if notification sent successfully
        """
        # Always log the notification
        logger.info(f"NOTIFICATION: {title} - {message}")

        # Send Discord notification
        if self._is_discord_configured():
            return await self.send_discord(message, title)
        else:
            logger.warning("Discord not configured. Set DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID.")
            return False

    def _is_discord_configured(self) -> bool:
        """Check if Discord is properly configured."""
        return self.bot_token and self.channel_id

    async def send_discord(self, message: str, title: str = "Scraper Alert") -> bool:
        """
        Send Discord notification.

        Args:
            message: The message to send
            title: The title/subject

        Returns:
            True if Discord message sent successfully
        """
        if not self._is_discord_configured():
            logger.warning("Discord not configured. Set DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID.")
            return False

        try:
            return await self._send_discord_message(message, title)

        except Exception as e:
            logger.error(f"Failed to send Discord message: {e}")
            return False

    async def _send_discord_message(self, message: str, title: str) -> bool:
        """
        Async method to send Discord message.

        Args:
            message: The message to send
            title: The title/subject

        Returns:
            True if message sent successfully
        """
        try:
            await self.client.login(self.bot_token)

            # Get the channel
            channel = self.client.get_channel(self.channel_id)
            if not channel:
                # If channel not in cache, fetch it
                channel = await self.client.fetch_channel(self.channel_id)

            if not channel:
                logger.error(f"Could not find Discord channel with ID: {self.channel_id}")
                return False

            # Create embed for better formatting
            embed = discord.Embed(
                title=title,
                description=message,
                color=0x00FF00,  # Green color
                timestamp=datetime.now(),
            )
            embed.set_footer(text="Scraper Bot")

            # Send the message
            await channel.send(embed=embed)

            logger.info(f"Discord message sent successfully to channel {self.channel_id}")
            return True

        except discord.errors.LoginFailure:
            logger.error("Failed to login to Discord. Check your DISCORD_BOT_TOKEN.")
            return False
        except discord.errors.Forbidden:
            logger.error("Bot doesn't have permission to send messages to the specified channel.")
            return False
        except discord.errors.NotFound:
            logger.error(f"Discord channel with ID {self.channel_id} not found.")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Discord message: {e}")
            return False
        finally:
            if not self.client.is_closed():
                await self.client.close()
