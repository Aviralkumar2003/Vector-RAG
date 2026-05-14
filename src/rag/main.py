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

    relevant_documents = rag_retriever.retrieve(query)

    model = ChatOpenAI(model=OPENAI_MODEL)
    # model = ChatOpenAI(model=OPENAI_MODEL, temperature=0.7)
    prompt = "User Query: " + query + "\n\n" + "Here are some relevant documents:\n" + "\n".join([doc["content"] for doc in relevant_documents]) + "\n\nBased on the above documents, please provide an answer to the user's query."
    response = model.invoke(prompt)
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
