import datetime
import logging
import os
import traceback
import typing
import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv


# This class extends commands.Bot, providing additional and customized functionality for the Discord bot.
class CustomBot(commands.Bot):
    # HTTP client session for making web requests
    client: aiohttp.ClientSession
    # Record the bot's startup time in UTC.
    _uptime: datetime.datetime = datetime.datetime.now(datetime.UTC)

    # Constructor of the CustomBot class. Called when an instance of the bot is created.
    def __init__(self, prefix: str, ext_dir: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        # Defines the common intents of the bot
        intents = discord.Intents.default()
        # Allows the bot to receive events related to members
        intents.members = True
        # # Allows the bot to receive events related to reactions to messages
        intents.reactions = True
        # Allows the bot to read the content of messages
        intents.message_content = True
        # Call the base class constructor
        super().__init__(*args, **kwargs, command_prefix=commands.when_mentioned_or(prefix), intents=intents)
        # Configure the logger for this instance of the bot
        self.logger = logging.getLogger(self.__class__.__name__)
        # Directory where cogs are located
        self.ext_dir = ext_dir
        # Flag to check whether slash command trees have been synchronized.
        self.synced = False

    # Async method for loading cogs
    async def _load_extensions(self) -> None:
        # Check if the cogs directory exists
        if not os.path.isdir(self.ext_dir):
            self.logger.error(f"Extension directory {self.ext_dir} does not exist.")
            return
        # Itera on all files in the extensions directory.
        for filename in os.listdir(self.ext_dir):
            # Check if the file ends with “.py” and does not start with “_” to ignore temporary or internal files
            if filename.endswith(".py") and not filename.startswith("_"):
                try:
                    # Load the extension using the full path
                    await self.load_extension(f"{self.ext_dir}.{filename[:-3]}")
                    self.logger.info(f"Loaded extension {filename[:-3]}")
                except commands.ExtensionError:
                    # Handles errors when loading an extension
                    self.logger.error(f"Failed to load extension {filename[:-3]}\n{traceback.format_exc()}")

    # Event that is called when an unhandled error occurs in an event
    async def on_error(self, event_method: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        # Log the error, including the full stack trace for debugging
        self.logger.error(f"An error occurred in {event_method}.\n{traceback.format_exc()}")

    # Event that is called when the bot is ready and connected to Discord
    async def on_ready(self) -> None:
        self.logger.info(f"Logged in as {self.user} ({self.user.id})")

    # Async method called during the bot setup process
    async def setup_hook(self) -> None:
        # Initialize the aiohttp client session
        self.client = aiohttp.ClientSession()
        # Load all extensions
        await self._load_extensions()
        # Sync the command tree slash with Discord.
        if not self.synced:
            # Sync slash commands globally
            await self.tree.sync()
            # Inverts the synced flag
            self.synced = not self.synced
            self.logger.info("Synced command tree")

    # Async method called when the bot is about to be closed
    async def close(self) -> None:
        # Call the close method of the base class
        await super().close()
        # Close the aiohttp client session
        await self.client.close()

    # Method to start the bot, Load the token from .env and start the Discord client
    def run(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        # Load environment variables from the .env file
        load_dotenv()
        try:
            # Start the bot using the Discord token from the environment
            super().run(str(os.getenv("TOKEN_DISCORD")), *args, **kwargs)
        except (discord.LoginFailure, KeyboardInterrupt):
            # Handles login errors or keyboard interruptions
            self.logger.info("Exiting...")
            exit()

    # Property to obtain the bot user object, Ensures that the bot is ready before returning the user object
    @property
    def user(self) -> discord.ClientUser:
        # Ensure that the bot is logged in
        assert super().user, "Bot is not ready yet"
        # Cast for type hinting
        return typing.cast(discord.ClientUser, super().user)

    # Properties for calculating bot uptime.
    @property
    def uptime(self) -> datetime.timedelta:
        return datetime.datetime.now(datetime.UTC) - self._uptime


# --- Main function ---
def main() -> None:
    # Configure basic logging
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
    # Create an instance of the bot with the prefix “!” and extensions in the “cogs” directory
    bot = CustomBot(prefix="!", ext_dir="cogs")
    # Start the bot.
    bot.run()


# Check if the script is executed directly.
if __name__ == "__main__":
    main()
