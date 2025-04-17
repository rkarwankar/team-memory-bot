# src/query_engine/engine.py
import logging
import json
from typing import Dict, List, Any
import openai  # Or import for Ollama if you're using that
from config import OPENAI_API_KEY, LLM_MODEL, TOP_K_RESULTS  # Adjust imports based on your setup
from memory.mem0 import query_memories
from memory.vector_store import query_vectors
from query_engine.rag import generate_rag_response

logger = logging.getLogger(__name__)

async def query_knowledge(query: str) -> str:
    """
    Query the knowledge system to answer a user's question.
    
    This function:
    1. Searches the vector store for semantically similar content
    2. Queries the Mem0 memory store for relevant memories
    3. Combines both results and generates a RAG response
    
    Args:
        query (str): The user's natural language query
        
    Returns:
        str: The generated response to the query
    """
    try:
        logger.info(f"Processing query: {query}")
        
        # Query both the vector store and Mem0 memory in parallel
        try:
            vector_results = await query_vectors(query, top_k=TOP_K_RESULTS)
            logger.info(f"Vector search returned {len(vector_results)} results")
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            vector_results = []
            
        try:
            mem0_results = await query_memories(query)
            logger.info(f"Mem0 search returned {len(mem0_results.get('memories', []))} results")
        except Exception as e:
            logger.error(f"Error querying memories: {e}")
            mem0_results = {"memories": []}
        
        # Combine and prepare context for RAG
        combined_context = prepare_context(vector_results, mem0_results)
        
        # Generate response using RAG
        if combined_context:
            response = await generate_rag_response(query, combined_context)
        else:
            response = "I don't have any information about that in the team memory yet."
        
        return response
        
    except Exception as e:
        logger.error(f"Error in query_knowledge: {e}", exc_info=True)
        return f"I encountered an error while searching the team memory: {str(e)}"

def prepare_context(vector_results: List[Dict[str, Any]], mem0_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Prepare and combine context from vector store and Mem0 results.
    
    Args:
        vector_results (List[Dict[str, Any]]): Results from vector store query
        mem0_results (Dict[str, Any]): Results from Mem0 memory query
        
    Returns:
        List[Dict[str, Any]]: Combined context for RAG
    """
    combined_context = []
    
    # Add vector results to context
    for result in vector_results:
        combined_context.append({
            "source": "vector_store",
            "id": result.get("id", "unknown"),
            "score": result.get("score", 0.0),
            "metadata": result.get("metadata", {}),
            "text": result.get("text", "")
        })
    
    # Add Mem0 results to context - updated for Mem0 service response format
    for memory in mem0_results.get("memories", []):
        combined_context.append({
            "source": "mem0",
            "id": memory.get("id", "unknown"),
            "type": memory.get("type", "unknown"),
            "summary": memory.get("summary", ""),
            "timestamp": memory.get("timestamp", ""),
            "context": memory.get("context", ""),
            "participants": memory.get("participants", [])
        })
    
    # Sort by relevance score if available, otherwise keep original order
    combined_context.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    
    return combined_context



async def format_memories_by_type(memory_type: str = None, limit: int = 5) -> str:
    """
    Format recent memories of a specific type for display.
    
    Args:
        memory_type (str, optional): Type of memory to filter
        limit (int, optional): Maximum number of memories to return
        
    Returns:
        str: Formatted text of recent memories
    """
    from memory.mem0 import get_recent_memories
    
    try:
        memories = await get_recent_memories(memory_type, limit)
        
        if not memories:
            return f"No recent {memory_type or 'memory'} items found."
        
        # Log memory count for debugging
        logger.info(f"Retrieved {len(memories)} memories of type {memory_type}")
        
        # Format memories as markdown
        formatted_text = ""
        
        for i, memory in enumerate(memories, 1):
            mem_type = memory.get("type", "unknown").upper()
            summary = memory.get("summary", "No summary available")
            timestamp = memory.get("timestamp", "Unknown time")
            context = memory.get("context", "")
            participants = ", ".join(memory.get("participants", []))
            
            # Log memory details for debugging
            logger.info(f"Memory {i}: type={mem_type}, summary={summary[:50]}...")
            
            formatted_text += f"{i}. **{mem_type}** ({timestamp})\n"
            formatted_text += f"{summary}\n"
            
            if context:
                formatted_text += f"*Context: {context}*\n"
                
            if participants:
                formatted_text += f"*Participants: {participants}*\n"
                
            formatted_text += "\n"
        
        return formatted_text
        
    except Exception as e:
        logger.error(f"Error formatting memories: {e}", exc_info=True)
        return f"Error retrieving memories: {str(e)}"
    


# async def format_memories_by_type(memory_type: str = None, limit: int = 5) -> str:
#     """
#     Format recent memories of a specific type for display.
    
#     Args:
#         memory_type (str, optional): Type of memory to filter
#         limit (int, optional): Maximum number of memories to return
        
#     Returns:
#         str: Formatted text of recent memories
#     """
#     from memory.mem0 import get_recent_memories
    
#     try:
#         memories = await get_recent_memories(memory_type, limit)
        
#         if not memories:
#             return f"No recent {memory_type or 'memory'} items found."
        
#         # Format memories as markdown
#         formatted_text = ""
        
#         for i, memory in enumerate(memories, 1):
#             memory_type = memory.get("type", "unknown")
#             summary = memory.get("summary", "No summary available")
#             timestamp = memory.get("timestamp", "Unknown time")
#             context = memory.get("context", "")
#             participants = ", ".join(memory.get("participants", []))
            
#             formatted_text += f"**{i}. {memory_type.upper()}** ({timestamp})\n"
#             formatted_text += f"{summary}\n"
            
#             if context:
#                 formatted_text += f"*Context: {context}*\n"
                
#             if participants:
#                 formatted_text += f"*Participants: {participants}*\n"
                
#             formatted_text += "\n"
        
#         return formatted_text
        
#     except Exception as e:
#         logger.error(f"Error formatting memories: {e}", exc_info=True)
#         return f"Error retrieving memories: {str(e)}"