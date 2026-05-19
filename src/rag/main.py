from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from config.config import OPENAI_MODEL
from src.rag.embedding_manager import EmbeddingManager
from src.rag.ingestion_pipeline import run_ingestion_pipeline
from src.rag.rag_retreiver import RAGRetriever
from src.rag.vector_store import VectorStore

from langsmith import traceable

load_dotenv()


def initialize_rag_system():
    """Initialize RAG system with one-time ingestion if needed."""
    embedding_manager = EmbeddingManager()
    vector_store = VectorStore()
    
    run_ingestion_pipeline(embedding_manager, vector_store)
    
    return RAGRetriever(vector_store, embedding_manager)


def get_llm_source(relevant_documents):
    source_list = []

    for doc in relevant_documents:
        page = doc["metadata"].get("page")

        if page is not None:
            source = f"Page {page + 1}"
        else:
            source = doc["metadata"].get("source", "")

        if source and source not in source_list:
            source_list.append(source)

    return ", ".join(source_list)


def get_rag_response(query: str, rag_retriever=None):
    if rag_retriever is None:
        rag_retriever = initialize_rag_system()

    relevant_documents = rag_retriever.retrieve(query, top_k=10, score_threshold=0.35)

    model = ChatOpenAI(model=OPENAI_MODEL)
    messages = [
        {
            "role": "system",
            "content": (
                # "You are a financial analyst assistant. Answer questions strictly based on "
                # "the provided document excerpts. When a numeric value is requested, reproduce "
                # "it exactly as it appears in the documents. If the documents do not contain "
                # "enough information to answer, say so explicitly — do not guess or extrapolate. "
                # "Cite the page number when available."
                "You are a helpful assistant. Answer questions strictly based on "
                "the provided document excerpts. If the documents do not contain "
                "enough information to answer, say so explicitly — do not guess or extrapolate. "
                "Cite the page number when available."
            )
        },
        {
            "role": "user",
            "content": (
                f"Question: {query}\n\n"
                "Document Excerpts:\n"
                + "\n\n---\n\n".join(
                    f"[Page {doc['metadata'].get('page', 0) + 1}, "
                    f"Type: {doc['metadata'].get('type', 'text')}]\n{doc['content']}"
                    for doc in relevant_documents
                )
                + "\n\nAnswer:"
            )
        }
    ]
    response = model.invoke(messages)
    llm_source = get_llm_source(relevant_documents)

    return {"answer": response.content, "source": llm_source, "documents": relevant_documents}


@traceable()
def run_retrieval_query(query: str, rag_retriever=None):
    result = get_rag_response(query, rag_retriever)

    print("---------------------------------------")
    print(result["answer"])
    return result


if __name__ == "__main__":

    query = "What was the net profit of Mercedes-Benz Group in 2022?"
    run_retrieval_query(query)
