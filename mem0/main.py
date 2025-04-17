import os
import json
import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import uvicorn
from sqlalchemy import create_engine, Column, String, JSON, DateTime, MetaData, Table, select, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Mem0 Memory API",
    description="API for storing and retrieving team knowledge memories",
    version="1.0.0",
)

# Configure database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:toor@localhost:5432/team_memory")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define Memory model
class Memory(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, index=True)
    type = Column(String, index=True)
    summary = Column(String)
    timestamp = Column(DateTime, index=True)
    context = Column(String)
    participants = Column(JSON)
    raw_content = Column(String, nullable=True)
    message_id = Column(String, nullable=True)
    channel_id = Column(String, nullable=True)
    author_id = Column(String, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Define Pydantic models for API
class MemoryCreate(BaseModel):
    type: str
    summary: str
    timestamp: str
    context: str
    participants: List[str]
    raw_content: Optional[str] = None
    message_id: Optional[str] = None
    channel_id: Optional[str] = None
    author_id: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class MemoryResponse(BaseModel):
    id: str
    type: str
    summary: str
    timestamp: str
    context: str
    participants: List[str]
    raw_content: Optional[str] = None
    message_id: Optional[str] = None
    channel_id: Optional[str] = None
    author_id: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    created_at: str

class QueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class QueryResponse(BaseModel):
    query: str
    memories: List[MemoryResponse]

# Helper functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def parse_timestamp(timestamp_str: str) -> datetime:
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except ValueError:
        try:
            return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError(f"Invalid timestamp format: {timestamp_str}")

# API endpoints
@app.post("/memories", response_model=MemoryResponse)
async def create_memory(memory: MemoryCreate):
    """
    Create a new memory entry in the Mem0 system.
    """
    try:
        memory_id = str(uuid.uuid4())
        
        # Parse timestamp
        timestamp = parse_timestamp(memory.timestamp)
        
        # Create memory object
        db_memory = Memory(
            id=memory_id,
            type=memory.type,
            summary=memory.summary,
            timestamp=timestamp,
            context=memory.context,
            participants=memory.participants,
            raw_content=memory.raw_content,
            message_id=memory.message_id,
            channel_id=memory.channel_id,
            author_id=memory.author_id,
            meta_data=memory.metadata,
            created_at=datetime.utcnow()
        )
        
        # Save to database
        db = SessionLocal()
        db.add(db_memory)
        db.commit()
        db.refresh(db_memory)
        db.close()
        
        return MemoryResponse(
            id=db_memory.id,
            type=db_memory.type,
            summary=db_memory.summary,
            timestamp=db_memory.timestamp.isoformat(),
            context=db_memory.context,
            participants=db_memory.participants,
            raw_content=db_memory.raw_content,
            message_id=db_memory.message_id,
            channel_id=db_memory.channel_id,
            author_id=db_memory.author_id,
            meta_data=db_memory.metadata,
            created_at=db_memory.created_at.isoformat()
        )
    except Exception as e:
        logger.error(f"Error creating memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memories/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: str):
    """
    Get a specific memory by ID.
    """
    db = SessionLocal()
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    db.close()
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return MemoryResponse(
        id=memory.id,
        type=memory.type,
        summary=memory.summary,
        timestamp=memory.timestamp.isoformat(),
        context=memory.context,
        participants=memory.participants,
        raw_content=memory.raw_content,
        message_id=memory.message_id,
        channel_id=memory.channel_id,
        author_id=memory.author_id,
        meta_data=memory.metadata,
        created_at=memory.created_at.isoformat()
    )

@app.post("/query", response_model=QueryResponse)
async def query_memories(query_request: QueryRequest):
    """
    Query memories using natural language.
    
    This is a simplified implementation that does basic keyword matching.
    In a production system, this would use semantic search or an LLM.
    """
    try:
        db = SessionLocal()
        
        # Simple keyword-based search (in production, replace with vector search)
        keywords = query_request.query.lower().split()
        results = []
        
        # Search in memory summaries and raw content
        memories = db.query(Memory).order_by(desc(Memory.timestamp)).limit(100).all()
        
        for memory in memories:
            # Check if any keyword matches in summary or raw content
            summary_lower = memory.summary.lower()
            raw_content_lower = memory.raw_content.lower() if memory.raw_content else ""
            
            matches = any(keyword in summary_lower or keyword in raw_content_lower for keyword in keywords)
            
            if matches:
                results.append(MemoryResponse(
                    id=memory.id,
                    type=memory.type,
                    summary=memory.summary,
                    timestamp=memory.timestamp.isoformat(),
                    context=memory.context,
                    participants=memory.participants,
                    raw_content=memory.raw_content,
                    message_id=memory.message_id,
                    channel_id=memory.channel_id,
                    author_id=memory.author_id,
                    meta_data=memory.metadata,
                    created_at=memory.created_at.isoformat()
                ))
            
            if len(results) >= query_request.limit:
                break
        
        db.close()
        
        return QueryResponse(
            query=query_request.query,
            memories=results
        )
    except Exception as e:
        logger.error(f"Error querying memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memories/recent", response_model=List[MemoryResponse])
async def get_recent_memories(
    type: Optional[str] = None,
    limit: int = Query(5, ge=1, le=50)
):
    """
    Get recent memories, optionally filtered by type.
    """
    try:
        db = SessionLocal()
        
        query = db.query(Memory).order_by(desc(Memory.timestamp))
        
        if type:
            query = query.filter(Memory.type == type)
        
        memories = query.limit(limit).all()
        
        results = []
        for memory in memories:
            results.append(MemoryResponse(
                id=memory.id,
                type=memory.type,
                summary=memory.summary,
                timestamp=memory.timestamp.isoformat(),
                context=memory.context,
                participants=memory.participants,
                raw_content=memory.raw_content,
                message_id=memory.message_id,
                channel_id=memory.channel_id,
                author_id=memory.author_id,
                meta_data=memory.metadata,
                created_at=memory.created_at.isoformat()
            ))
        
        db.close()
        
        return results
    except Exception as e:
        logger.error(f"Error getting recent memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """
    Root endpoint - health check.
    """
    return {"status": "ok", "service": "Mem0 Memory API", "version": "1.0.0"}

# Run the server if executed directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
