import logging
import os
import json
import httpx
from typing import List, Dict, Any, Optional
import asyncio
from config import (
    VECTOR_DB, PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME,
    CHROMADB_PERSIST_DIRECTORY, EMBEDDING_MODEL, OPENAI_API_KEY, OLLAMA_API_URL
)

logger = logging.getLogger(__name__)

# Global variable to hold the vector store client
_vector_client = None

async def initialize_vector_db():
    """Initialize the vector database based on configuration."""
    global _vector_client
    
    if VECTOR_DB.lower() == "pinecone":
        await initialize_pinecone()
    elif VECTOR_DB.lower() == "chromadb":
        await initialize_chromadb()
    else:
        raise ValueError(f"Unsupported vector database: {VECTOR_DB}")

async def initialize_pinecone():
    """Initialize Pinecone vector database."""
    try:
        # Import here to avoid requiring pinecone when using chromadb
        from pinecone import Pinecone
        
        # Initialize Pinecone with the new API structure
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Check if index exists, create it if not
        indexes = pc.list_indexes()
        index_names = [index.name for index in indexes]
        
        if PINECONE_INDEX_NAME not in index_names:
            logger.info(f"Creating Pinecone index: {PINECONE_INDEX_NAME}")
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=1536,  # OpenAI embedding dimensions
                metric="cosine"
            )
        
        # Connect to the index
        index = pc.Index(PINECONE_INDEX_NAME)
        
        global _vector_client
        _vector_client = {
            "type": "pinecone",
            "client": index
        }
        
        logger.info("Pinecone initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing Pinecone: {e}", exc_info=True)
        raise

async def initialize_chromadb():
    """Initialize ChromaDB vector database."""
    try:
        # Import here to avoid requiring pinecone when using chromadb
        from pinecone import Pinecone
        
        # Initialize Pinecone with the new API structure
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Check if index exists, create it if not
        indexes = pc.list_indexes()
        index_names = [index.name for index in indexes]
        
        if PINECONE_INDEX_NAME not in index_names:
            logger.info(f"Creating Pinecone index: {PINECONE_INDEX_NAME}")
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=1536,  # OpenAI embedding dimensions
                metric="cosine"
            )
        
        # Connect to the index
        index = pc.Index(PINECONE_INDEX_NAME)
        
        global _vector_client
        _vector_client = {
            "type": "pinecone",
            "client": index
        }
        
        logger.info("Pinecone initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing Pinecone: {e}", exc_info=True)
        raise


async def get_embedding(text: str) -> List[float]:
    """
    Generate a simple embedding vector for text without using external APIs.
    
    This is a fallback method that creates a deterministic but non-semantic embedding.
    
    Args:
        text (str): Text to embed
        
    Returns:
        List[float]: Simple embedding vector
    """
    try:
        # Try to use Ollama if available
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{OLLAMA_API_URL}/api/embeddings",
                    json={
                        "model": EMBEDDING_MODEL,
                        "prompt": text
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    embedding = result.get("embedding", [])
                    
                    # If embedding exists and has proper length
                    if embedding and len(embedding) > 0:
                        # Resize if needed
                        if len(embedding) > 1536:
                            embedding = embedding[:1536]
                        elif len(embedding) < 1536:
                            embedding = embedding + [0.0] * (1536 - len(embedding))
                        
                        return embedding
        except Exception as e:
            logger.warning(f"Could not use Ollama embedding API: {e}, using fallback method")
        
        # Fallback: Create a simple deterministic vector based on text content
        import hashlib
        
        # Generate a hash of the text
        hasher = hashlib.md5(text.encode('utf-8'))
        hash_bytes = hasher.digest()
        
        # Convert hash to list of floats
        hash_ints = [b for b in hash_bytes]
        
        # Expand to 1536 dimensions (OpenAI's dimension)
        embedding = []
        for i in range(1536):
            val = hash_ints[i % len(hash_ints)] / 255.0
            embedding.append(val)
        
        return embedding
        
    except Exception as e:
        logger.error(f"Error generating embedding: {e}", exc_info=True)
        # Return a zero vector as fallback
        return [0.0] * 1536
    

async def store_vector(memory_id: str, text: str, metadata: Dict[str, Any]):
    """
    Store a vector embedding in the vector database.
    
    Args:
        memory_id (str): Unique ID for the memory
        text (str): Text to embed and store
        metadata (Dict[str, Any]): Additional metadata to store with the vector
    """
    if _vector_client is None:
        try:
            await initialize_vector_db()
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {e}")
            return  # Skip vector storage if we can't initialize
    
    try:
        # Get embedding for the text
        embedding = await get_embedding(text)
        
        if _vector_client["type"] == "pinecone":
            # Store in Pinecone with updated API
            try:
                _vector_client["client"].upsert(
                    vectors=[
                        {"id": memory_id, "values": embedding, "metadata": metadata}
                    ],
                    namespace="team-memory"
                )
                logger.debug(f"Stored vector in Pinecone for memory_id: {memory_id}")
            except Exception as e:
                logger.error(f"Error storing vector in Pinecone: {e}")
                
        elif _vector_client["type"] == "chromadb":
            # Store in ChromaDB
            try:
                _vector_client["client"].upsert(
                    ids=[memory_id],
                    embeddings=[embedding],
                    metadatas=[metadata],
                    documents=[text]
                )
                logger.debug(f"Stored vector in ChromaDB for memory_id: {memory_id}")
            except Exception as e:
                logger.error(f"Error storing vector in ChromaDB: {e}")
        
    except Exception as e:
        logger.error(f"Error storing vector: {e}", exc_info=True)

async def query_vectors(query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Query vectors by similarity.
    
    Args:
        query_text (str): Text to search for
        top_k (int): Number of results to return
        
    Returns:
        List[Dict[str, Any]]: List of matching memories with their metadata
    """
    if _vector_client is None:
        try:
            await initialize_vector_db()
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {e}")
            return []  # Return empty list if we can't initialize
    
    try:
        # Get embedding for the query
        embedding = await get_embedding(query_text)
        
        if _vector_client["type"] == "pinecone":
            # Query Pinecone with updated API
            try:
                results = _vector_client["client"].query(
                    vector=embedding,
                    top_k=top_k,
                    include_metadata=True,
                    namespace="team-memory"
                )
                
                # Format results for new Pinecone API
                matches = []
                for match in results.matches:
                    matches.append({
                        "id": match.id,
                        "score": match.score,
                        "metadata": match.metadata
                    })
                
                return matches
            except Exception as e:
                logger.error(f"Error querying Pinecone: {e}")
                return []
            
        elif _vector_client["type"] == "chromadb":
            # Query ChromaDB
            try:
                results = _vector_client["client"].query(
                    query_embeddings=[embedding],
                    n_results=top_k
                )
                
                # Format results
                matches = []
                for i, (doc_id, document, metadata, distance) in enumerate(zip(
                    results["ids"][0],
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    matches.append({
                        "id": doc_id,
                        "score": 1.0 - distance,  # Convert distance to similarity score
                        "metadata": metadata,
                        "text": document
                    })
                
                return matches
            except Exception as e:
                logger.error(f"Error querying ChromaDB: {e}")
                return []
        
        return []
        
    except Exception as e:
        logger.error(f"Error querying vectors: {e}", exc_info=True)
        return []










# async def get_embedding(text: str) -> List[float]:
#     """
#     Generate an embedding vector for the given text using Ollama.
    
#     Args:
#         text (str): Text to embed
        
#     Returns:
#         List[float]: Embedding vector
#     """
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 f"{OLLAMA_API_URL}/api/embeddings",
#                 json={
#                     "model": EMBEDDING_MODEL,
#                     "prompt": text
#                 },
#                 timeout=30.0
#             )
            
#             response.raise_for_status()
#             result = response.json()
#             embedding = result.get("embedding", [])
            
#             # If the embedding doesn't have 1536 dimensions, resize it
#             if len(embedding) != 1536:
#                 # Either truncate or pad to 1536 dimensions
#                 if len(embedding) > 1536:
#                     embedding = embedding[:1536]
#                 else:
#                     embedding = embedding + [0.0] * (1536 - len(embedding))
            
#             return embedding
            
#     except Exception as e:
#         logger.error(f"Error generating embedding: {e}", exc_info=True)
#         # Return a zero vector as fallback
#         return [0.0] * 1536

# async def store_vector(memory_id: str, text: str, metadata: Dict[str, Any]):
#     """
#     Store a vector embedding in the vector database.
    
#     Args:
#         memory_id (str): Unique ID for the memory
#         text (str): Text to embed and store
#         metadata (Dict[str, Any]): Additional metadata to store with the vector
#     """
#     if _vector_client is None:
#         await initialize_vector_db()
    
#     try:
#         # Get embedding for the text
#         embedding = await get_embedding(text)
        
#         if _vector_client["type"] == "pinecone":
#             # Store in Pinecone with updated API
#             _vector_client["client"].upsert(
#                 vectors=[
#                     {"id": memory_id, "values": embedding, "metadata": metadata}
#                 ],
#                 namespace="team-memory"
#             )
#         elif _vector_client["type"] == "chromadb":
#             # Store in ChromaDB
#             _vector_client["client"].upsert(
#                 ids=[memory_id],
#                 embeddings=[embedding],
#                 metadatas=[metadata],
#                 documents=[text]
#             )
        
#         logger.debug(f"Stored vector for memory_id: {memory_id}")
        
#     except Exception as e:
#         logger.error(f"Error storing vector: {e}", exc_info=True)

# async def query_vectors(query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
#     """
#     Query vectors by semantic similarity.
    
#     Args:
#         query_text (str): Text to search for
#         top_k (int): Number of results to return
        
#     Returns:
#         List[Dict[str, Any]]: List of matching memories with their metadata
#     """
#     if _vector_client is None:
#         await initialize_vector_db()
    
#     try:
#         # Get embedding for the query
#         embedding = await get_embedding(query_text)
        
#         if _vector_client["type"] == "pinecone":
#             # Query Pinecone with updated API
#             results = _vector_client["client"].query(
#                 vector=embedding,
#                 top_k=top_k,
#                 include_metadata=True,
#                 namespace="team-memory"
#             )
            
#             # Format results for new Pinecone API
#             matches = []
#             for match in results.matches:
#                 matches.append({
#                     "id": match.id,
#                     "score": match.score,
#                     "metadata": match.metadata
#                 })
            
#             return matches
            
#         elif _vector_client["type"] == "chromadb":
#             # Query ChromaDB
#             results = _vector_client["client"].query(
#                 query_embeddings=[embedding],
#                 n_results=top_k
#             )
            
#             # Format results
#             matches = []
#             for i, (doc_id, document, metadata, distance) in enumerate(zip(
#                 results["ids"][0],
#                 results["documents"][0],
#                 results["metadatas"][0],
#                 results["distances"][0]
#             )):
#                 matches.append({
#                     "id": doc_id,
#                     "score": 1.0 - distance,  # Convert distance to similarity score
#                     "metadata": metadata,
#                     "text": document
#                 })
            
#             return matches
        
#     except Exception as e:
#         logger.error(f"Error querying vectors: {e}", exc_info=True)
#         return []