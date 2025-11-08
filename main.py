"""
Discord Economy Bot - Main Entry Point
A feature-rich economy bot with leveling, gambling, and more!
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.database import Database
from utils.config import Config

# setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('EconomyBot')


class EconomyBot(commands.Bot):
    """Custom bot class with additional functionality"""
    
    def __init__(self):
        # bot intents - we need most of them for full functionality
        intents = discord.Intents.all()
        
        # initialize the bot
        super().__init__(
            command_prefix=commands.when_mentioned_or(Config.PREFIX),
            intents=intents,
            help_command=None,  # we'll make our own
            case_insensitive=True
        )
        
        self.config = Config
        self.db: Optional[Database] = None
        self.start_time = discord.utils.utcnow()
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Starting bot setup...")
        
        # initialize database
        self.db = Database()
        await self.db.setup()
        logger.info("Database initialized")
        
        # load all cogs
        await self.load_cogs()
        
        # sync commands if guild id is provided
        if Config.GUILD_ID:
            guild = discord.Object(id=Config.GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f"Commands synced to guild {Config.GUILD_ID}")
        else:
            await self.tree.sync()
            logger.info("Commands synced globally")
            
    async def load_cogs(self):
        """Load all cog modules"""
        cogs_dir = Path("cogs")
        
        if not cogs_dir.exists():
            logger.error("Cogs directory not found!")
            return
            
        for file in cogs_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue
                
            cog_name = f"cogs.{file.stem}"
            try:
                await self.load_extension(cog_name)
                logger.info(f"Loaded cog: {cog_name}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog_name}: {e}")
                
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        logger.info("Bot is ready!")
        
        # set activity
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{Config.PREFIX}help | /help"
        )
        await self.change_presence(activity=activity)
        
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Global error handler for text commands"""
        if isinstance(error, commands.CommandNotFound):
            return
            
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
            return
            
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument provided")
            return
            
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ This command is on cooldown. Try again in {error.retry_after:.1f}s")
            return
            
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command")
            return
            
        # log unexpected errors
        logger.error(f"Unexpected error in command {ctx.command}: {error}", exc_info=error)
        await ctx.send("❌ An unexpected error occurred. Please try again later.")
        
    async def close(self):
        """Cleanup when bot is shutting down"""
        logger.info("Shutting down bot...")
        
        if self.db:
            await self.db.close()
            
        await super().close()


def main():
    """Main entry point"""
    # load environment variables
    load_dotenv()
    
    # check for token
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("No DISCORD_TOKEN found in environment variables!")
        logger.error("Please create a .env file with your bot token")
        sys.exit(1)
        
    # create and run bot
    bot = EconomyBot()
    
    try:
        bot.run(token, log_handler=None)  # we set up our own logging
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
