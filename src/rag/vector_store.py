import os
from typing import Any, List
import uuid

import chromadb
import numpy as np


class VectorStore:
    def __init__(self, collection_name:str="pdf_documents",persist_directory:str="./data/vector_store"):
        self.collection_name=collection_name
        self.persist_directory=persist_directory
        self.client=None
        self.collection=None
        self._intitialize_store()

    def _intitialize_store(self):
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)

            self.collection=self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "description": "PDF Document Embdeddings for RAG",
                }
            )

            print(f"Vector store initialized with collection: {self.collection_name}")
            print(f"Existing documents in collection: {self.collection.count()}")

        except Exception as e:
            print(f"Error initializing vector store: {e}")
            raise
                

    def add_documents(self, documents: List[Any], embeddings: np.ndarray):
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents and embeddings must match.")
        
        print(f"Adding {len(documents)} documents to vector store.")
        ids=[]
        metadatas=[]
        documents_text=[]
        embeddings_list=[]

        for i, (doc,embedding) in enumerate(zip(documents,embeddings)):
            doc_id=f"doc_{uuid.uuid4().hex[:8]}_{i}"
            ids.append(doc_id)

            metadata=dict(doc.metadata)
            metadata['doc_index']=i
            metadata['content_length']=len(doc.page_content)
            metadatas.append(metadata)

            documents_text.append(doc.page_content)

            embeddings_list.append(embedding.tolist())

        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=documents_text
            )
            print(f"Successfully added {len(documents)} documents to vector store.")
            print(f"Total documents in collection after addition: {self.collection.count()}")
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            raise 
