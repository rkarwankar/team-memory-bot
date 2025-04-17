import discord
from discord.ext import commands
import logging
import asyncio
from query_engine.engine import query_knowledge
from preprocessing.extractor import extract_knowledge
from preprocessing.classifier import classify_message
from memory.mem0 import store_memory
from config import MEMORY_TYPES

logger = logging.getLogger(__name__)

class MemoryCommands(commands.Cog):
    """Commands for interacting with the Team Memory Bot."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="ask", help="Ask a question about team knowledge")
    async def ask(self, ctx, *, question):
        """
        Query the team knowledge memory.
        
        Args:
            question (str): Natural language question to ask the memory system
        """
        async with ctx.typing():
            try:
                # Inform user that processing is happening
                processing_msg = await ctx.send("Processing your question... 🧠")
                
                # Get response from query engine
                response = await query_knowledge(question)
                
                # Create embed for nicer display
                embed = discord.Embed(
                    title="Memory Response",
                    description=response,
                    color=discord.Color.blue()
                )
                embed.set_footer(text="Based on team memory records")
                
                await processing_msg.delete()
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error processing query: {e}", exc_info=True)
                await ctx.send(f"Sorry, I encountered an error: {str(e)}")
    
    @commands.command(name="save", help="Save important knowledge to team memory")
    async def save(self, ctx, type_arg, *, content):
        """
        Manually save knowledge to team memory.
        
        Args:
            type_arg (str): Type of memory (decision, blocker, etc.)
            content (str): Content to save to memory
        """
        # Validate memory type
        memory_type = type_arg.lower()
        if memory_type not in MEMORY_TYPES:
            valid_types = ", ".join(MEMORY_TYPES)
            await ctx.send(f"Invalid memory type. Please use one of: {valid_types}")
            return
        
        async with ctx.typing():
            try:
                # Extract knowledge summary
                knowledge_summary = await extract_knowledge(content)
                
                # Store in memory
                memory_entry = {
                    "type": memory_type,
                    "summary": knowledge_summary,
                    "timestamp": ctx.message.created_at.isoformat(),
                    "context": f"channel: {ctx.channel.name} (manual save)",
                    "participants": [f"@{ctx.author.name}"],
                    "raw_content": content,
                    "message_id": str(ctx.message.id),
                    "channel_id": str(ctx.channel.id),
                    "author_id": str(ctx.author.id)
                }
                
                await store_memory(memory_entry)
                
                # Confirmation message
                embed = discord.Embed(
                    title="Memory Saved",
                    description=f"**Type:** {memory_type}\n**Summary:** {knowledge_summary}",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error saving memory: {e}", exc_info=True)
                await ctx.send(f"Sorry, I encountered an error: {str(e)}")
    
    @commands.command(name="recent", help="Show recent memories of a specific type")
    async def recent(self, ctx, memory_type=None, limit: int = 5):
        """
        Display recent memories of a specific type.
        
        Args:
            memory_type (str, optional): Type of memory to filter by
            limit (int, optional): Number of memories to retrieve (default: 5)
        """
        # If the first argument is a number, it's the limit, not the memory type
        if memory_type and memory_type.isdigit():
            limit = int(memory_type)
            memory_type = None
            
        # Validate memory type if provided
        if memory_type and memory_type.lower() not in MEMORY_TYPES:
            valid_types = ", ".join(MEMORY_TYPES)
            await ctx.send(f"Invalid memory type. Please use one of: {valid_types}")
            return
                
        async with ctx.typing():
            try:
                # Get formatted memories
                from query_engine.engine import format_memories_by_type
                response = await format_memories_by_type(memory_type, limit)
                
                # Create embed for nicer display
                title = f"Recent {memory_type or 'Memory'} Items"
                embed = discord.Embed(
                    title=title,
                    description=response,
                    color=discord.Color.blue()
                )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error retrieving recent memories: {e}", exc_info=True)
                await ctx.send(f"Sorry, I encountered an error: {str(e)}")
    
    @commands.command(name="help_memory", help="Show help information about the memory bot")
    async def help_memory(self, ctx):
        """Display help information about the memory bot."""
        embed = discord.Embed(
            title="Team Memory Bot Help",
            description="I'm your team's knowledge memory bot. I track important information from your conversations.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="How I Work",
            value="I monitor conversations in designated channels and automatically extract important information. "
                  "You can also manually save memories or query existing ones.",
            inline=False
        )
        
        embed.add_field(
            name="Commands",
            value=(
                f"`{ctx.prefix}ask [question]` - Ask a question about team knowledge\n"
                f"`{ctx.prefix}save [type] [content]` - Manually save knowledge\n"
                f"`{ctx.prefix}recent [type] [limit]` - Show recent memories\n"
                f"`{ctx.prefix}help_memory` - Show this help message"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Memory Types",
            value=", ".join(MEMORY_TYPES),
            inline=False
        )
        
        embed.add_field(
            name="Example Questions",
            value=(
                "• What decisions were made in the last 2 standups?\n"
                "• When did we decide to deprecate feature X?\n"
                "• What blockers are still unresolved?\n"
                "• What's the status of the frontend work?"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Add the commands cog to the bot."""
    await bot.add_cog(MemoryCommands(bot))
    logger.info("Memory commands registered")