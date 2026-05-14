from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client

import pandas as pd

from config.config import DATASET_PATH
from src.rag.main import initialize_rag_system, run_retrieval_query


load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

client = Client()

excel_file = DATASET_PATH
dataset_name = "Vector RAG"


def get_dataset():
    df = pd.read_excel(excel_file)

    questions_list = df["Question"].tolist()
    reference_answer_list = df["Reference_Answer"].tolist()
    source_list = df["Source"].tolist()

    dataset = [
        {
            "inputs": {"query": question},
            "outputs": {
                "answer": answer,
                "source": source
            }
        }
        for question, answer, source in zip(
            questions_list,
            reference_answer_list,
            source_list
        )
    ]

    return df, dataset


def populate_llm_response_and_source():
    df, dataset = get_dataset()
    rag_retriever = initialize_rag_system()
    llm_response_list = []
    llm_source_list = []
    llm_results = {}

    for item in dataset:
        result = run_retrieval_query(item["inputs"]["query"], rag_retriever)
        llm_response_list.append(result["answer"])
        llm_source_list.append(result["source"])
        llm_results[item["inputs"]["query"]] = result

    df["LLM_Response"] = llm_response_list
    df["LLM_Source"] = llm_source_list
    df.to_excel(excel_file, index=False)
    return llm_results


def create_langsmith_dataset():
    _, dataset = get_dataset()

    # Delete existing dataset to avoid mixing old and new examples
    if client.has_dataset(dataset_name=dataset_name):
        langsmith_dataset = client.read_dataset(dataset_name=dataset_name)
        client.delete_dataset(dataset_id=langsmith_dataset.id)
    
    # Create fresh dataset with current examples
    langsmith_dataset = client.create_dataset(dataset_name=dataset_name)

    client.create_examples(
        dataset_id=langsmith_dataset.id,
        examples=dataset
    )

    return langsmith_dataset
