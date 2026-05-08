
from chunking import split_documents
from embedding_manager import EmbeddingManager
import load_documents
from vector_store import VectorStore


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
    documents=load_documents.load_pdf_documents("pdfs")
    chunks=split_documents(documents, chunk_size=1000, chunk_overlap=200)
    texts=[doc.page_content for doc in chunks]

    embeddings=embedding_manager.generate_embeddings(texts)
    
    vector_store.add_documents(chunks, embeddings)
    print("Ingestion pipeline completed successfully.")