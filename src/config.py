import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord configuration
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")
MONITORED_CHANNELS = os.getenv("MONITORED_CHANNELS", "").split(",")

# LLM configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = "gpt-3.5-turbo" # Use this model for the free tier
EMBEDDING_MODEL = "text-embedding-ada-002" # OpenAI's embedding model

# Ollama configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:latest")  # or whichever Llama model you have
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "llama3.1:latest")  # Using same model for embeddings

# Vector database configuration
VECTOR_DB = os.getenv("VECTOR_DB", "pinecone")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "team-memory")
CHROMADB_PERSIST_DIRECTORY = os.getenv("CHROMADB_PERSIST_DIRECTORY", "./chroma_db")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
# REDIS_URL = os.getenv("REDIS_URL")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Mem0 Memory Engine
# MEM0_API_URL = os.getenv("MEM0_API_URL", "https://app.mem0.ai/api")
MEM0_API_KEY = os.getenv("MEM0_API_KEY", "")

# Memory types
MEMORY_TYPES = ["decision", "blocker", "status_update", "milestone", "question", "answer"]

# Command prefix
COMMAND_PREFIX = "/"

# RAG configuration
EMBEDDING_MODEL = "text-embedding-3-large"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_TOKENS = 4096
TOP_K_RESULTS = 5