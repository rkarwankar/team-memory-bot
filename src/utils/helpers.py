import logging
import json
import datetime
from typing import Dict, List, Any, Optional, Union
import uuid

logger = logging.getLogger(__name__)

def generate_memory_id() -> str:
    """
    Generate a unique ID for a memory entry.
    
    Returns:
        str: Unique memory ID
    """
    return str(uuid.uuid4())

def format_timestamp(timestamp: Optional[Union[str, datetime.datetime]] = None) -> str:
    """
    Format a timestamp in a consistent way.
    
    Args:
        timestamp: Timestamp to format (string or datetime)
        
    Returns:
        str: Formatted timestamp
    """
    if timestamp is None:
        timestamp = datetime.datetime.now()
        
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.datetime.fromisoformat(timestamp)
        except ValueError:
            # If parsing fails, return the original string
            return timestamp
    
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def safe_json_loads(json_str: str) -> Dict[str, Any]:
    """
    Safely parse JSON string, returning empty dict on failure.
    
    Args:
        json_str (str): JSON string to parse
        
    Returns:
        Dict[str, Any]: Parsed JSON or empty dict
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Error parsing JSON: {e}")
        return {}

def format_memory_for_display(memory: Dict[str, Any]) -> str:
    """
    Format a memory entry for display in Discord.
    
    Args:
        memory (Dict[str, Any]): Memory entry to format
        
    Returns:
        str: Formatted string
    """
    memory_type = memory.get("type", "unknown").upper()
    summary = memory.get("summary", "No summary available")
    timestamp = format_timestamp(memory.get("timestamp"))
    context = memory.get("context", "")
    participants = ", ".join(memory.get("participants", []))
    
    formatted = f"**{memory_type}** ({timestamp})\n"
    formatted += f"{summary}\n"
    
    if context:
        formatted += f"*Context: {context}*\n"
        
    if participants:
        formatted += f"*Participants: {participants}*\n"
        
    return formatted

def chunk_text(text: str, chunk_size: int = 2000) -> List[str]:
    """
    Chunk text into Discord-friendly chunks (max 2000 chars).
    
    Args:
        text (str): Text to chunk
        chunk_size (int): Maximum chunk size
        
    Returns:
        List[str]: List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    for line in text.split("\n"):
        # If line itself is too long, split it further
        if len(line) > chunk_size:
            while line:
                space_to_take = min(chunk_size - len(current_chunk), len(line))
                current_chunk += line[:space_to_take]
                line = line[space_to_take:]
                
                if len(current_chunk) >= chunk_size:
                    chunks.append(current_chunk)
                    current_chunk = ""
        else:
            # Check if adding this line would exceed the chunk size
            if len(current_chunk) + len(line) + 1 > chunk_size:  # +1 for newline
                chunks.append(current_chunk)
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"
    
    # Add the last chunk if it has content
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks
