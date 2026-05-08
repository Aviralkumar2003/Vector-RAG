from langchain_openai import ChatOpenAI

from embedding_manager import EmbeddingManager
from ingestion_pipeline import run_ingestion_pipeline
from rag_retreiver import RAGRetriever
from vector_store import VectorStore

from langsmith import traceable


def initialize_rag_system():
    """Initialize RAG system with one-time ingestion if needed."""
    embedding_manager = EmbeddingManager()
    vector_store = VectorStore()
    
    run_ingestion_pipeline(embedding_manager, vector_store)
    
    return RAGRetriever(vector_store, embedding_manager)

@traceable()
def run_retrieval_query(query: str):
    rag_retriever = initialize_rag_system()
    relevant_documents = rag_retriever.retrieve(query)
    
    model = ChatOpenAI(model="gpt-5.4", temperature=0.7)
    prompt = "User Query: " + query + "\n\n" + "Here are some relevant documents:\n" + "\n".join([doc["content"] for doc in relevant_documents]) + "\n\nBased on the above documents, please provide an answer to the user's query."
    response = model.invoke(prompt)
    
    print("---------------------------------------")
    print(response.content)
    return {"answer":response.content, "documents": relevant_documents}


if __name__ == "__main__":
    
    # Example Queries (can run multiple times without re-ingesting):
    # What amount of unrealized gain on non-marketable equity securities accounted for under the measurement alternative was recognized in Q1 2026?
    # Which acquisition primarily affected Google Cloud and in what way, and what was its purchase price?
    # What was the total cash, cash equivalents, and marketable securities balance at March 31, 2026?
    # Which business segment contributed the largest share of operating income in Q1 2026?
    # What amount of unrealized gain on non-marketable equity securities accounted for under the measurement alternative was recognized in Q1 2026?

    query = "Which acquisition primarily affected Google Cloud and in what way, and what was its purchase price?"
    run_retrieval_query(query)