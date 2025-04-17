import discord
from discord.ext import commands
import logging
from config import DISCORD_BOT_TOKEN, COMMAND_PREFIX, MONITORED_CHANNELS

logger = logging.getLogger(__name__)

class MemoryBot(commands.Bot):
    """Custom Discord bot class for Team Knowledge Memory Bot."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guild_messages = True
        
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=commands.DefaultHelpCommand(),
        )
        
        self.monitored_channels = MONITORED_CHANNELS
        
    async def setup_hook(self):
        """Load command and event extensions when the bot starts."""
        from bot.commands import setup
        await setup(self)
        
        from bot.listeners import setup_listeners
        setup_listeners(self)
        
        logger.info("Bot extensions and listeners loaded")
        
    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Monitoring channels: {', '.join(self.monitored_channels)}")
        
        # Set bot activity
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="team conversations"
        )
        await self.change_presence(activity=activity)
    
    async def start(self):
        """Start the bot with the configured token."""
        await super().start(DISCORD_BOT_TOKEN)

def create_bot():
    """Create and configure the Discord bot instance."""
    return MemoryBot()