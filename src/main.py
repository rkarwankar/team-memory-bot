import asyncio
import logging
import sys
from bot.client import create_bot
from memory.vector_store import initialize_vector_db
from config import LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Initialize and run the Discord bot and related services."""
    logger.info("Starting Team Memory Bot...")
    
    # Initialize vector database
    logger.info("Initializing vector database...")
    await initialize_vector_db()
    
    # Create and run Discord bot
    logger.info("Initializing Discord bot...")
    bot = create_bot()
    
    logger.info("Team Memory Bot is running!")
    await bot.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown by user")
    except Exception as e:
        logger.error(f"Error in main process: {e}", exc_info=True)
        sys.exit(1)