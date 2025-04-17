import logging
from typing import Dict, List, Any, Optional
import asyncio
import uuid
from config import MEM0_API_KEY

logger = logging.getLogger(__name__)

# Import the Mem0 client
try:
    from mem0 import MemoryClient
    MEM0_AVAILABLE = True
except ImportError:
    logger.error("mem0ai package not installed. Please install with: pip install mem0ai")
    MEM0_AVAILABLE = False

class Mem0Wrapper:
    """Wrapper for the official Mem0 MemoryClient that provides async functionality."""
    
    def __init__(self, api_key: str):
        """Initialize with API key."""
        if not MEM0_AVAILABLE:
            logger.error("mem0ai package not installed. Cannot initialize client.")
            return
            
        self.client = MemoryClient(api_key=api_key)
        self.loop = asyncio.get_event_loop()
    
    async def add_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store a memory entry in the Mem0 system.
        
        Args:
            memory (Dict[str, Any]): Memory data to store
            
        Returns:
            Dict[str, Any]: Response from the Mem0 API
        """
        try:
            # Extract information from memory to format for Mem0
            memory_type = memory.get("type", "status_update")
            summary = memory.get("summary", "")
            raw_content = memory.get("raw_content", summary)
            author = memory.get("participants", ["unknown"])[0].replace("@", "")
            
            # Format as messages for Mem0
            messages = [
                {"role": "user", "content": raw_content},
                {"role": "assistant", "content": f"I've recorded this {memory_type}: {summary}"}
            ]
            
            # Use a consistent user_id for all team memory
            user_id = "team_memory_default"
            
            # Additional metadata
            metadata = {
                "type": memory_type,
                "timestamp": memory.get("timestamp", ""),
                "context": memory.get("context", ""),
                "message_id": memory.get("message_id", ""),
                "channel_id": memory.get("channel_id", ""),
                "author": author
            }
            
            # Run the synchronous Mem0 client in a thread pool
            return await self.loop.run_in_executor(
                None, 
                lambda: self.client.add(messages, user_id=user_id, metadata=metadata)
            )
        except Exception as e:
            logger.error(f"Error storing memory in Mem0: {e}", exc_info=True)
            raise
    
    async def search_memories(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Query memories from the Mem0 system.
        
        Args:
            query (str): Natural language query
            user_id (str, optional): User ID to limit search scope
            
        Returns:
            Dict[str, Any]: Response with matching memories
        """
        try:
            # Use a default user_id if none provided
            if not user_id:
                user_id = "team_memory_default"
            
            # Search the Mem0 API
            results = await self.loop.run_in_executor(
                None,
                lambda: self.client.search(query, user_id=user_id)
            )
            
            # Log the results for debugging
            logger.info(f"Raw search results: {results}")
            
            formatted_results = {"memories": []}
            
            # Process each result from Mem0
            if isinstance(results, list):
                for result in results:
                    # Extract the actual memory content
                    memory_content = result.get("memory", "")
                    
                    # Get metadata
                    metadata = result.get("metadata", {})
                    
                    # Create formatted memory object
                    memory = {
                        "id": result.get("id", str(uuid.uuid4())),
                        "type": metadata.get("type", "status_update"),
                        "summary": memory_content,  # Use the memory content as summary
                        "timestamp": metadata.get("timestamp", ""),
                        "context": metadata.get("context", ""),
                        "participants": [metadata.get("author", "unknown")],
                    }
                    
                    formatted_results["memories"].append(memory)
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error querying memories from Mem0: {e}", exc_info=True)
            return {"memories": []}
    
    async def get_recent_memories(self, memory_type: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent memories, optionally filtered by type.
        
        Args:
            memory_type (str, optional): Type of memory to filter by
            limit (int, optional): Maximum number of memories to return
            
        Returns:
            List[Dict[str, Any]]: List of recent memories
        """
        try:
            # Need a non-empty query for Mem0
            base_query = "recent memories"
            query = f"{memory_type} {base_query}" if memory_type else base_query
            
            user_id = "team_memory_default"
            
            # Use search as a way to get all memories
            results = await self.loop.run_in_executor(
                None,
                lambda: self.client.search(query, user_id=user_id)
            )
            
            logger.info(f"Raw get_recent_memories results: {results}")
            
            memories = []
            
            if isinstance(results, list):
                for result in results:
                    # Extract memory content
                    memory_content = result.get("memory", "")
                    metadata = result.get("metadata", {})
                    
                    # Create memory object
                    memory = {
                        "id": result.get("id", str(uuid.uuid4())),
                        "type": metadata.get("type", "status_update"),
                        "summary": memory_content,  # Use memory content as summary
                        "timestamp": metadata.get("timestamp", ""),
                        "context": metadata.get("context", ""),
                        "participants": [metadata.get("author", "unknown")],
                    }
                    
                    # Only add if matches requested type
                    if not memory_type or memory.get("type") == memory_type:
                        memories.append(memory)
                
                # Sort by timestamp, newest first
                memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                
                # Limit number of results
                memories = memories[:limit]
            
            return memories
        except Exception as e:
            logger.error(f"Error getting recent memories: {e}", exc_info=True)
            return []
        

        
# Global client instance
_mem0_client = None

def get_mem0_client() -> Mem0Wrapper:
    """
    Get or create the global Mem0 client instance.
    
    Returns:
        Mem0Wrapper: The Mem0 client wrapper instance
    """
    global _mem0_client
    if _mem0_client is None:
        _mem0_client = Mem0Wrapper(api_key=MEM0_API_KEY)
    return _mem0_client

# Module-level functions that can be imported directly

async def store_memory(memory: Dict[str, Any]) -> Dict[str, Any]:
    """
    Store a memory in the Mem0 system.
    
    Args:
        memory (Dict[str, Any]): Memory data to store
        
    Returns:
        Dict[str, Any]: Response from the Mem0 API
    """
    client = get_mem0_client()
    try:
        return await client.add_memory(memory)
    except Exception as e:
        logger.error(f"Error in store_memory: {e}", exc_info=True)
        return {}

async def query_memories(query: str) -> Dict[str, Any]:
    """
    Query memories from the Mem0 system.
    
    Args:
        query (str): Natural language query
        
    Returns:
        Dict[str, Any]: Response with matching memories
    """
    client = get_mem0_client()
    try:
        return await client.search_memories(query)
    except Exception as e:
        logger.error(f"Error in query_memories: {e}", exc_info=True)
        return {"memories": []}

async def get_recent_memories(memory_type: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get recent memories, optionally filtered by type.
    
    Args:
        memory_type (str, optional): Type of memory to filter by
        limit (int, optional): Maximum number of memories to return
        
    Returns:
        List[Dict[str, Any]]: List of recent memories
    """
    client = get_mem0_client()
    try:
        return await client.get_recent_memories(memory_type, limit)
    except Exception as e:
        logger.error(f"Error in get_recent_memories: {e}", exc_info=True)
        return []