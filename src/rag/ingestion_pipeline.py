
import os

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm

from src.rag.chunking import process_tables, split_documents
from config.config import DATA_DIR
from src.rag.embedding_manager import EmbeddingManager
from src.rag import load_documents
from src.rag.vector_store import VectorStore


def should_run_ingestion(vector_store: VectorStore) -> bool:
    """Check if ingestion should run based on whether vector store already has documents."""
    document_count = vector_store.collection.count()
    if document_count > 0:
        print(f"Vector store already contains {document_count} documents. Skipping ingestion.")
        return False
    return True


def run_ingestion_pipeline(embedding_manager: EmbeddingManager, vector_store: VectorStore):
    """Run ingestion pipeline only if vector store is empty."""
    if not should_run_ingestion(vector_store):
        return
    
    print("Starting ingestion pipeline...")
    documents=load_documents.load_pdf_documents(DATA_DIR)


    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=300,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    items = []

    for doc in tqdm(documents, desc="Processing PDF Pages"):
        filepath = os.path.join(DATA_DIR, doc.metadata.get("source", "_"))

        process_tables(doc, items, filepath)
        split_documents(doc, text_splitter, items, filepath)

    # Convert items (dict format) to Document objects for consistent handling
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

    # Extract text content for embeddings
    texts = [item["text"] for item in items]
    
    # Generate embeddings for all content (tables + text)
    embeddings = embedding_manager.generate_embeddings(texts)
    
    # Add documents and embeddings to vector store
    vector_store.add_documents(doc_objects, embeddings)
    print("Ingestion pipeline completed successfully.")