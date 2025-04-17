import logging
import httpx
from config import OLLAMA_API_URL, LLM_MODEL, MEMORY_TYPES

logger = logging.getLogger(__name__)

# Simple keywords for different types of memories (fallback method)
KEYWORDS = {
    "decision": ["decided", "decision", "choose", "selected", "agreed", "conclusion"],
    "blocker": ["blocked", "blocker", "issue", "problem", "impediment", "stuck", "delayed"],
    "status_update": ["update", "status", "progress", "completed", "working on", "started"],
    "milestone": ["milestone", "achieved", "finished", "released", "shipped", "launched"],
    "question": ["?", "how", "what", "when", "why", "where", "who", "which", "can", "could"],
    "answer": ["answer", "solution", "resolved", "fixed", "solved"]
}
# For src/preprocessing/classifier.py:
async def classify_message(text: str) -> str:
    """
    Classify a message using keyword matching.
    
    Args:
        text (str): The message text to classify
        
    Returns:
        str: The classified memory type
    """
    if not text or len(text.strip()) < 10:
        return "status_update"  # Default for short messages
    
    text_lower = text.lower()
    
    # Simple keyword-based classification
    if any(word in text_lower for word in ["decided", "decision", "choose", "agree", "conclusion"]):
        return "decision"
    elif any(word in text_lower for word in ["blocked", "blocker", "issue", "problem", "impediment"]):
        return "blocker"
    elif any(word in text_lower for word in ["complete", "milestone", "finished", "released"]):
        return "milestone"
    elif "?" in text or any(word in text_lower for word in ["how", "what", "when", "why", "where"]):
        return "question"
    elif any(word in text_lower for word in ["answer", "solution", "resolved", "fixed"]):
        return "answer"
    else:
        return "status_update"  # Default type
# async def classify_message(text: str) -> str:
#     """
#     Classify a message into a memory type (decision, blocker, etc.) using Ollama.
    
#     Args:
#         text (str): The message text to classify
        
#     Returns:
#         str: The classified memory type
#     """
#     if not text or len(text.strip()) < 10:
#         return "status_update"  # Default classification for short messages
    
#     try:
#         # Format memory types for prompt
#         memory_types_str = ", ".join(MEMORY_TYPES)
        
#         prompt = f"""
#         Classify the following message into one of these types: {memory_types_str}.
        
#         Here are guidelines for each type:
#         - decision: Contains a conclusion or choice made by the team
#         - blocker: Identifies an obstacle or impediment to progress
#         - status_update: Provides information about current progress
#         - milestone: Marks completion of a significant project phase
#         - question: Asks for information or clarification
#         - answer: Provides information in response to a question
        
#         Message: {text}
        
#         Classification (single word only):
#         """
        
#         try:
#             # Use Ollama API to generate a response
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     f"{OLLAMA_API_URL}/api/generate",
#                     json={
#                         "model": LLM_MODEL,
#                         "prompt": prompt
#                     }
#                 )
                
#                 response.raise_for_status()
#                 result = response.json()
#                 classification = result.get("response", "").strip().lower()
                
#                 # Validate against known types
#                 if classification not in MEMORY_TYPES:
#                     # Fall back to keyword-based classification
#                     classification = keyword_classify(text)
            
#             return classification
            
#         except Exception as e:
#             logger.error(f"Error with Ollama: {e}")
#             # Fall back to keyword-based classification
#             return keyword_classify(text)
            
#     except Exception as e:
#         logger.error(f"Error in message classification: {e}", exc_info=True)
#         return "status_update"  # Default classification on error

def keyword_classify(text: str) -> str:
    """Simple fallback classification based on keywords."""
    text_lower = text.lower()
    scores = {}
    
    # Score each type based on keyword matches
    for memory_type, keywords in KEYWORDS.items():
        score = 0
        for keyword in keywords:
            score += text_lower.count(keyword.lower())
        scores[memory_type] = score
    
    # Find type with highest score
    max_score = 0
    max_type = "status_update"  # Default
    
    for memory_type, score in scores.items():
        if score > max_score:
            max_score = score
            max_type = memory_type
    
    return max_type