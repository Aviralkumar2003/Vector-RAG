import asyncio
import json
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import AsyncGenerator, Optional, List, Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import dotenv

from src.rag.embedding_manager import EmbeddingManager
from src.rag.load_documents import load_pdf_documents
from src.rag.chunking import process_tables, split_documents
from src.rag.vector_store import VectorStore
from src.rag.rag_retreiver import RAGRetriever
from src.rag.database import db_manager
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

# Load environment variables
dotenv.load_dotenv()

# ============================================================================
# Session Management & Global State
# ============================================================================

@dataclass
class Session:
    """Represents a single PDF upload session."""
    session_id: str
    filename: str
    filepath: str
    status: str  # pending | processing | ready | error
    retriever: Optional[RAGRetriever] = None
    error_message: Optional[str] = None


# In-memory session store
sessions: Dict[str, Session] = {}

# Shared embedding manager (loaded once at startup)
embedding_manager: Optional[EmbeddingManager] = None


# ============================================================================
# FastAPI App Setup
# ============================================================================

app = FastAPI(title="AskMyPdf API", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Startup & Shutdown Events (Lifespan)
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize the EmbeddingManager on app startup."""
    global embedding_manager
    try:
        print("\n" + "="*60)
        print("🚀 Starting AskMyPdf API...")
        print("="*60)
        embedding_manager = EmbeddingManager()
        print(f"✅ Embedding model loaded successfully!")
        print("="*60 + "\n")
    except Exception as e:
        print(f"❌ Failed to load embedding model: {e}")
        raise


# ============================================================================
# Helper Functions
# ============================================================================

def sse_event(data: Dict[str, Any]) -> str:
    """Format a dictionary as a Server-Sent Event."""
    return f"data: {json.dumps(data)}\n\n"


# ============================================================================
# Pydantic Models
# ============================================================================

class ChatRequest(BaseModel):
    query: str
    session_id: str


# ============================================================================
# Endpoints
# ============================================================================

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and create a new session.
    
    Returns:
        {"session_id": str, "filename": str}
    """
    try:
        # Validate file is PDF
        if file.content_type != "application/pdf" or not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a valid PDF"
            )
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create upload directory
        upload_dir = Path("data/pdfs")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        filepath = upload_dir / f"{session_id}_{file.filename}"
        contents = await file.read()
        
        with open(filepath, "wb") as f:
            f.write(contents)
        
        # Create session
        session = Session(
            session_id=session_id,
            filename=file.filename,
            filepath=str(filepath),
            status="pending"
        )
        sessions[session_id] = session
        
        # Persist to database
        db_manager.save_session(
            session_id=session_id,
            filename=file.filename,
            filepath=str(filepath),
            status="pending"
        )
        
        print(f"\n📄 Session created: {session_id}")
        print(f"   File: {file.filename}")
        print(f"   Status: pending\n")
        
        return {
            "session_id": session_id,
            "filename": file.filename
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )


@app.get("/process/{session_id}")
async def process_pdf(session_id: str):
    """
    Process a PDF and stream progress via Server-Sent Events.
    
    Runs the RAG ingestion pipeline:
    1. Load PDF documents
    2. Extract tables
    3. Split/chunk documents
    4. Generate embeddings
    5. Store in vector store
    6. Create RAGRetriever
    """
    # Validate session exists
    if session_id not in sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    session = sessions[session_id]
    
    # Check if already processing or ready
    if session.status in ["processing", "ready"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Session already {session.status}"
        )
    
    # Start processing
    return StreamingResponse(
        ingest_pdf_stream(session),
        media_type="text/event-stream"
    )


async def ingest_pdf_stream(session: Session) -> AsyncGenerator[str, None]:
    """
    Async generator that yields SSE events during PDF ingestion.
    
    Emits progress at each stage:
    - loading: 15%
    - tables: 35%
    - chunking: 50%
    - embedding: 80%
    - storing: 95%
    - complete: 100%
    """
    try:
        session.status = "processing"
        db_manager.update_session_status(session.session_id, "processing")
        print(f"\n⚙️  Processing session {session.session_id}...")
        
        # Stage 1: Load documents
        print("   📂 Loading PDF documents...")
        yield sse_event({
            "type": "stage",
            "stage": "loading",
            "message": "Loading PDF pages...",
            "progress": 15
        })
        await asyncio.sleep(0.1)
        documents = load_pdf_documents(session.filepath)
        
        if not documents:
            session.status = "error"
            session.error_message = "No documents could be loaded from the PDF. It might be empty or corrupted."
            print(f"❌ Error: {session.error_message}")
            yield sse_event({
                "type": "error",
                "message": session.error_message
            })
            return

        # Stage 2: Process tables
        print("   📊 Processing tables...")
        yield sse_event({
            "type": "stage",
            "stage": "tables",
            "message": "Extracting tables...",
            "progress": 35
        })
        await asyncio.sleep(0.1)
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=300,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        items = []
        for doc in documents:
            process_tables(doc, items, session.filepath)
        
        # Stage 3: Split/chunk documents
        print("   ✂️  Splitting documents...")
        yield sse_event({
            "type": "stage",
            "stage": "chunking",
            "message": "Chunking text...",
            "progress": 50
        })
        await asyncio.sleep(0.1)
        
        for doc in documents:
            split_documents(doc, text_splitter, items, session.filepath)
        
        # Create Document objects
        doc_objects = [
            Document(
                page_content=item["text"],
                metadata={
                    "page": item["page"],
                    "type": item["type"],
                    "path": item["path"],
                    "source": item["source"]
                }
            )
            for item in items
        ]
        
        # Stage 4: Generate embeddings
        print("   🔢 Generating embeddings...")
        yield sse_event({
            "type": "stage",
            "stage": "embedding",
            "message": "Generating embeddings...",
            "progress": 80
        })
        await asyncio.sleep(0.1)
        
        texts = [item["text"] for item in items]
        embeddings = embedding_manager.generate_embeddings(texts)
        
        # Stage 5: Store in vector store
        print("   💾 Storing in vector store...")
        yield sse_event({
            "type": "stage",
            "stage": "storing",
            "message": "Storing in vector store...",
            "progress": 95
        })
        await asyncio.sleep(0.1)
        
        vector_store = VectorStore(collection_name=session.session_id)
        vector_store.add_documents(doc_objects, embeddings)
        
        # Stage 6: Create retriever and mark ready
        print("   🎯 Creating retriever...")
        session.retriever = RAGRetriever(vector_store, embedding_manager)
        session.status = "ready"
        db_manager.update_session_status(session.session_id, "ready")
        
        yield sse_event({
            "type": "complete",
            "message": "Ready to chat!",
            "progress": 100
        })
        
        print(f"✅ Session {session.session_id} ready for chat\n")
    
    except Exception as e:
        session.status = "error"
        session.error_message = str(e)
        db_manager.update_session_status(session.session_id, "error")
        print(f"❌ Error processing session {session.session_id}: {e}\n")
        yield sse_event({
            "type": "error",
            "message": f"Ingestion failed: {str(e)}"
        })


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Stream a chat response for a query against a processed PDF.
    
    Uses Server-Sent Events to stream tokens as they're generated.
    """
    # Check if session exists in memory
    if request.session_id not in sessions:
        # Check if it exists in database
        session_data = db_manager.get_session(request.session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {request.session_id} not found"
            )
        
        # Re-initialize session in memory
        sessions[request.session_id] = Session(
            session_id=request.session_id,
            filename=session_data["filename"],
            filepath=session_data["filepath"],
            status=session_data["status"]
        )
    
    session = sessions[request.session_id]
    
    # Check session is ready
    if session.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Session is {session.status}, not ready for chat"
        )
    
    # Check retriever is available, if not re-initialize it
    if session.retriever is None:
        try:
            print(f"🔄 Re-initializing retriever for session {request.session_id}...")
            vector_store = VectorStore(collection_name=request.session_id)
            session.retriever = RAGRetriever(vector_store, embedding_manager)
            print(f"✅ Retriever re-initialized")
        except Exception as e:
            print(f"❌ Failed to re-initialize retriever: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize retriever: {str(e)}"
            )
    
    return StreamingResponse(
        stream_chat_response(request, session),
        media_type="text/event-stream"
    )


async def stream_chat_response(request: ChatRequest, session: Session) -> AsyncGenerator[str, None]:
    """
    Async generator that yields SSE events during chat response streaming.
    
    Emits:
    - token events with content chunks
    - sources event with cited pages
    - complete event when done
    - error event if exception occurs
    """
    try:
        print(f"\n💬 Chat query: {request.query}")
        print(f"   Session: {request.session_id}")
        
        # Emit initial status
        yield sse_event({
            "type": "status",
            "content": "Searching PDF for relevant context..."
        })
        await asyncio.sleep(0.1)

        # Retrieve relevant chunks
        retrieved_docs = session.retriever.retrieve(
            request.query,
            top_k=10,
            score_threshold=0.35
        )
        
        if not retrieved_docs:
            yield sse_event({
                "type": "error",
                "message": "No relevant documents found in PDF"
            })
            return
        
        # Emit analysis status
        yield sse_event({
            "type": "status",
            "content": "Analyzing relevant chunks..."
        })
        await asyncio.sleep(0.1)

        # Build context from retrieved chunks with metadata headers
        context_blocks = []
        pages = set()
        sources = set()

        for doc in retrieved_docs:
            metadata = doc.get("metadata", {})
            page_num = metadata.get("page", 0)
            doc_type = metadata.get("type", "text")
            source_file = metadata.get("source", "Unknown Source")
            
            pages.add(page_num + 1)
            sources.add(source_file)
            
            header = f"[Source: {source_file}, Page: {page_num + 1}, Type: {doc_type}]"
            context_blocks.append(f"{header}\n{doc['content']}")

        context = "\n\n---\n\n".join(context_blocks)
        
        # Emit generation status
        yield sse_event({
            "type": "status",
            "content": "Generating response..."
        })
        await asyncio.sleep(0.1)

        # Build messages for OpenAI
        # system_message = """You are a helpful assistant that answers questions about the provided PDF document. 
# Use the context provided to answer the user's query. Be accurate and cite specific pages when relevant.
# If you cannot find the answer in the document, say so clearly."""
        
        # user_message = f"""Context from the PDF:
# {context}

# User question: {request.query}"""

        system_message = "You are a helpful assistant. Answer questions strictly based on the provided document excerpts. Always cite the source and page number for each piece of information you provide. If the documents do not contain enough information to answer, say so explicitly — do not guess or extrapolate."
        
        user_message = f"Question: {request.query}\n\nDocument Excerpts:\n{context}\n\nAnswer:"
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Stream response from OpenAI
        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            streaming=True,
            temperature=0.7
        )
        
        # Collect full response for logging
        full_response = ""
        
        async for chunk in llm.astream(messages):
            if chunk.content:
                full_response += chunk.content
                yield sse_event({
                    "type": "token",
                    "content": chunk.content
                })
        
        # Emit sources
        source_citations = []
        if sources:
            source_list = sorted(list(sources))
            pages_list = sorted(list(pages))
            
            sources_str = ", ".join(source_list)
            pages_str = ", ".join(map(str, pages_list))
            
            source_citations.append(f"Source(s): {sources_str}")
            source_citations.append(f"Page(s): {pages_str}")
        
        final_sources = " | ".join(source_citations) if source_citations else "Source information not available"
        
        yield sse_event({
            "type": "sources",
            "content": final_sources
        })
        
        # Emit complete
        yield sse_event({"type": "complete"})

        # Persist conversation to database
        db_manager.save_message(request.session_id, "user", request.query)
        db_manager.save_message(request.session_id, "assistant", full_response, final_sources)
        
        print(f"✅ Chat response streamed ({len(full_response)} chars)\n")
    
    except Exception as e:
        print(f"❌ Chat error: {e}\n")
        yield sse_event({
            "type": "error",
            "message": f"Chat failed: {str(e)}"
        })


@app.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """Retrieve chat history for a session from the database."""
    # Check if session exists in DB
    session_data = db_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    # If session is in DB but not in memory, we should ideally re-initialize it
    # For now, we just return history. Chat will fail if retriever isn't loaded.
    if session_id not in sessions and session_data["status"] == "ready":
        sessions[session_id] = Session(
            session_id=session_id,
            filename=session_data["filename"],
            filepath=session_data["filepath"],
            status="ready"
        )
        # We'll need to re-initialize the retriever when needed or here
        # For simplicity, let's just mark it as ready. 
        # The chat endpoint should handle re-initializing retriever if missing.
    
    messages = db_manager.get_messages(session_id)
    return {
        "session_id": session_id,
        "filename": session_data["filename"],
        "messages": messages
    }


@app.get("/sessions")
async def list_sessions():
    """List all available chat sessions."""
    return db_manager.get_all_sessions()


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its history."""
    # Check if exists
    session_data = db_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    # Delete from DB
    db_manager.delete_session(session_id)
    
    # Remove from memory if present
    if session_id in sessions:
        del sessions[session_id]
        
    return {"status": "success", "message": f"Session {session_id} deleted"}


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "ok",
        "embedding_model_loaded": embedding_manager is not None,
        "active_sessions": len([s for s in sessions.values() if s.status != "error"])
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
