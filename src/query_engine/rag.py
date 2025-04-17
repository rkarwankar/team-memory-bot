import logging
import json
from typing import Dict, List, Any
import httpx
from config import OLLAMA_API_URL, LLM_MODEL, MAX_TOKENS

logger = logging.getLogger(__name__)
async def generate_rag_response(query: str, context: List[Dict[str, Any]]) -> str:
    """
    Generate a response based on retrieved context.
    
    Args:
        query (str): The user's query
        context (List[Dict[str, Any]]): Context information retrieved from memory
        
    Returns:
        str: Generated response
    """
    try:
        if not context:
            return "I don't have any information about that in the team memory yet."
            
        # Check for tech stack related queries
        tech_stack_query = any(term in query.lower() for term in 
            ["tech stack", "technology", "stack", "framework", "angular", "react", "node", "frontend", "backend"])
        
        # Filter decisions if tech stack query
        if tech_stack_query:
            tech_decisions = [item for item in context if 
                (item.get("source") == "mem0" and item.get("type") == "decision") or
                (item.get("source") == "vector_store" and item.get("metadata", {}).get("type") == "decision")]
            
            # Use tech decisions if found
            if tech_decisions:
                filtered_context = tech_decisions
            else:
                filtered_context = context
        else:
            filtered_context = context
        
        # Generate a clear response
        response = "Based on our team memory:\n\n"
        
        for i, item in enumerate(filtered_context[:3], 1):  # Limit to top 3 results
            if item.get("source") == "vector_store":
                metadata = item.get("metadata", {})
                text = item.get("text", "No content available")
                type_str = metadata.get("type", "unknown").upper()
                date = metadata.get("timestamp", "")
                
                response += f"{i}. **{type_str}** ({date})\n"
                response += f"{text}\n\n"
                
            elif item.get("source") == "mem0":
                # Get the actual content of the memory from the result
                mem_type = item.get("type", "unknown").upper()
                content = item.get("summary", "")
                date = item.get("timestamp", "")
                
                response += f"{i}. **{mem_type}** ({date})\n"
                response += f"{content}\n\n"
        
        return response
    except Exception as e:
        logger.error(f"Error generating response: {e}", exc_info=True)
        return "I'm sorry, I couldn't generate a response based on the team memory."
    




# async def generate_rag_response(query: str, context: List[Dict[str, Any]]) -> str:
#     """
#     Generate a response using Retrieval-Augmented Generation (RAG) with Ollama.
    
#     Args:
#         query (str): The user's query
#         context (List[Dict[str, Any]]): Context information retrieved from memory
        
#     Returns:
#         str: Generated response
#     """
#     try:
#         # Format context for the prompt
#         formatted_context = format_context_for_prompt(context)
        
#         # Create the full prompt
#         prompt = f"""
# I need you to answer a question based on the team's memory records.

# Question: {query}

# Here are the relevant memory records from the team's history:

# {formatted_context}

# Please provide a clear, concise answer based ONLY on the information in these memory records.
# If the records don't contain enough information to answer the question, please state that clearly.
# Cite specific memories when appropriate by referring to their type and date.
# """
        
#         system_prompt = """You are an intelligent team memory assistant that helps teams recall their 
# decisions, blockers, and other important information. You should answer questions based solely on the 
# provided context. If the context doesn't contain the answer, say so clearly rather than guessing. 
# Format your responses in a clear, concise, and helpful way. For dates and times, use a consistent 
# and human-readable format."""
        
#         # Generate response using Ollama
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 f"{OLLAMA_API_URL}/api/generate",
#                 json={
#                     "model": LLM_MODEL,
#                     "prompt": prompt,
#                     "system": system_prompt,
#                     "stream": False,
#                     "options": {
#                         "temperature": 0.3,
#                         "num_predict": MAX_TOKENS
#                     }
#                 },
#                 timeout=60.0
#             )
            
#             response.raise_for_status()
#             result = response.json()
#             generated_text = result.get("response", "").strip()
        
#         return generated_text
        
#     except Exception as e:
#         logger.error(f"Error in RAG generation: {e}", exc_info=True)
#         return "I'm sorry, I couldn't generate a response based on the team memory."

def format_context_for_prompt(context: List[Dict[str, Any]]) -> str:
    """
    Format the context information for inclusion in the prompt.
    
    Args:
        context (List[Dict[str, Any]]): Context information
        
    Returns:
        str: Formatted context string
    """
    formatted_context = ""
    
    for i, item in enumerate(context, 1):
        if item.get("source") == "vector_store":
            # Format vector store item
            metadata = item.get("metadata", {})
            text = item.get("text", "No content available")
            
            formatted_context += f"MEMORY {i}:\n"
            formatted_context += f"Type: {metadata.get('type', 'unknown')}\n"
            formatted_context += f"Date: {metadata.get('timestamp', 'unknown')}\n"
            formatted_context += f"Content: {text}\n"
            if "participants" in metadata:
                formatted_context += f"Participants: {', '.join(metadata.get('participants', []))}\n"
            formatted_context += "\n"
            
        elif item.get("source") == "mem0":
            # Format Mem0 item
            formatted_context += f"MEMORY {i}:\n"
            formatted_context += f"Type: {item.get('type', 'unknown')}\n"
            formatted_context += f"Date: {item.get('timestamp', 'unknown')}\n"
            formatted_context += f"Content: {item.get('summary', 'No summary available')}\n"
            formatted_context += f"Context: {item.get('context', 'No context available')}\n"
            if "participants" in item:
                formatted_context += f"Participants: {', '.join(item.get('participants', []))}\n"
            formatted_context += "\n"
    
    return formatted_context

def create_rag_prompt(query: str, context: str) -> str:
    """
    Create the full prompt for RAG.
    
    Args:
        query (str): The user's query
        context (str): Formatted context information
        
    Returns:
        str: Complete prompt for the LLM
    """
    return f"""
I need you to answer a question based on the team's memory records.

Question: {query}

Here are the relevant memory records from the team's history:

{context}

Please provide a clear, concise answer based ONLY on the information in these memory records.
If the records don't contain enough information to answer the question, please state that clearly.
Cite specific memories when appropriate by referring to their type and date.
"""
