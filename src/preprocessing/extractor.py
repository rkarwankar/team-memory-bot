import logging
import httpx
import json
from config import OLLAMA_API_URL, LLM_MODEL

logger = logging.getLogger(__name__)


async def extract_knowledge(text: str) -> str:
    """
    Extract key knowledge from a text message using simple rules.
    
    Args:
        text (str): The raw text message to analyze
        
    Returns:
        str: A concise summary of the extracted knowledge
    """
    if not text or len(text.strip()) < 10:
        logger.debug("Text too short for knowledge extraction")
        return ""
    
    try:
        # Simple approach: use the first sentence or first part of the text
        sentences = text.split(".")
        if not sentences:
            return ""
            
        # Take the first sentence or part of the text
        if len(sentences[0]) > 100:
            summary = sentences[0][:100] + "..."
        else:
            summary = sentences[0] + "."
            
        return summary.strip()
        
    except Exception as e:
        logger.error(f"Error in knowledge extraction: {e}", exc_info=True)
        return text[:100]  # Return first 100 chars as fallback
# async def extract_knowledge(text: str) -> str:
#     """
#     Extract key knowledge from a text message using Ollama's Llama model.
    
#     Args:
#         text (str): The raw text message to analyze
        
#     Returns:
#         str: A concise summary of the extracted knowledge
#     """
#     if not text or len(text.strip()) < 10:
#         logger.debug("Text too short for knowledge extraction")
#         return ""
    
#     try:
#         prompt = f"""
#         You are a knowledge extraction AI that identifies important team information from messages. 
#         Extract the key knowledge, decisions, or blockers from the following message.
#         If there's nothing important, respond with "No significant knowledge".
        
#         Provide a concise summary in 1-2 sentences that captures the essence.
        
#         Message: {text}
        
#         Extracted knowledge:
#         """
        
#         # Simplified Ollama request to minimize errors
#         async with httpx.AsyncClient(timeout=60.0) as client:
#             try:
#                 response = await client.post(
#                     f"{OLLAMA_API_URL}/api/generate",
#                     json={
#                         "model": LLM_MODEL,
#                         "prompt": prompt
#                     }
#                 )
                
#                 response.raise_for_status()
#                 result = response.json()
#                 extraction = result.get("response", "").strip()
                
#             except httpx.HTTPStatusError as e:
#                 logger.error(f"HTTP error {e.response.status_code} from Ollama: {e.response.text}")
#                 # Fallback to simple extraction
#                 sentences = text.split(".")
#                 extraction = sentences[0] if sentences else text[:100]
                
#             except Exception as e:
#                 logger.error(f"Error calling Ollama: {str(e)}")
#                 # Fallback to simple extraction
#                 sentences = text.split(".")
#                 extraction = sentences[0] if sentences else text[:100]
        
#         # If the model determines there's no significant knowledge, return empty string
#         if "No significant knowledge" in extraction:
#             return ""
            
#         return extraction
        
#     except Exception as e:
#         logger.error(f"Error in knowledge extraction: {e}", exc_info=True)
#         # Fallback to simple extraction
#         sentences = text.split(".")
#         return sentences[0] if sentences else text[:100]