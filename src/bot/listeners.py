import discord
import logging
import asyncio
from discord.ext import commands
from preprocessing.extractor import extract_knowledge
from preprocessing.classifier import classify_message
from memory.mem0 import store_memory
from config import MONITORED_CHANNELS

logger = logging.getLogger(__name__)

async def process_message(message):
    """
    Process a Discord message to extract and store knowledge.
    
    Args:
        message (discord.Message): The Discord message to process
    """
    # Skip messages from bots to avoid feedback loops
    if message.author.bot:
        return
    
    # Skip messages not in monitored channels
    if str(message.channel.id) not in MONITORED_CHANNELS:
        return
    
    try:
        # Extract knowledge from message
        knowledge_summary = await extract_knowledge(message.content)
        
        # Skip if no meaningful knowledge extracted
        if not knowledge_summary:
            return
        
        # Classify message type
        message_type = await classify_message(message.content)
        
        # Store in memory
        memory_entry = {
            "type": message_type,
            "summary": knowledge_summary,
            "timestamp": message.created_at.isoformat(),
            "context": f"channel: {message.channel.name}",
            "participants": [f"@{message.author.name}"],
            "raw_content": message.content,
            "message_id": str(message.id),
            "channel_id": str(message.channel.id),
            "author_id": str(message.author.id)
        }
        
        await store_memory(memory_entry)
        logger.debug(f"Stored memory: {memory_entry['type']} - {memory_entry['summary']}")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)

async def on_message(message):
    """Event handler for new messages."""
    # We'll process the message in the background to not block the bot
    asyncio.create_task(process_message(message))

def setup_listeners(bot):
    """Register event listeners for the bot."""
    
    @bot.event
    async def on_message(message):
        # Process commands first
        await bot.process_commands(message)
        # Then process for knowledge extraction
        await process_message(message)
    
    logger.info("Message listeners registered")