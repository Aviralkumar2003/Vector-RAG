# RAG — Retrieval-Augmented Generation for Financial Documents

A RAG pipeline that ingests PDF documents (e.g. annual reports), extracts both plain text and structured tables separately, embeds them with a sentence transformer, stores them in a persistent ChromaDB vector store, and answers natural-language queries using an OpenAI LLM — with full LangSmith tracing and an LLM-based evaluation suite.

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| Java (JDK) | 11+ (required by `tabula-py` for table extraction) |

Verify both are on your `PATH`:

```bash
python --version
java -version
```

---

## Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd RAG
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Copy the example file and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env`:

```env
OPENAI_API_KEY=sk-...

# LangSmith (optional — only needed for tracing and evaluation)
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=ls__...
LANGSMITH_PROJECT=My First App

# Java home for tabula-py table extraction
JAVA_HOME=C:\Program Files\Java\jdk-21
```

> `JAVA_HOME` must point to a valid JDK installation. On Windows this is typically `C:\Program Files\Java\jdk-<version>`.

---

## Project Structure

```
RAG/
├── config/
│   └── config.py              # Central constants (model name, data paths)
├── src/
│   └── rag/
│       ├── load_documents.py  # PDF loading via PyMuPDF
│       ├── chunking.py        # Table extraction + text chunking
│       ├── embedding_manager.py  # Sentence-transformer embeddings
│       ├── vector_store.py    # ChromaDB wrapper
│       ├── ingestion_pipeline.py # Orchestrates one-time ingestion
│       ├── rag_retreiver.py   # Cosine-similarity retrieval
│       └── main.py            # Entry point — query → LLM answer
├── tests/
│   ├── evaluation.py          # Dataset management + LangSmith upload
│   └── evaluators.py          # 4 LLM-based evaluators
├── data/
│   ├── pdfs/                  # ← place your PDF files here
│   ├── processed_data/
│   │   ├── processed_tables/  # Extracted table text files
│   │   └── processed_text/    # Chunked text files
│   ├── vector_store/          # ChromaDB persistent storage
│   └── dataset/
│       └── dataset.xlsx       # Evaluation Q&A dataset
├── .env.example
└── requirements.txt
```

---

## Adding Documents

Place your PDF files inside `data/pdfs/`. The ingestion pipeline will automatically detect and process all `.pdf` files in that directory (including subdirectories) on the **first run**. Subsequent runs skip ingestion if the vector store already contains documents.

```
data/pdfs/
└── mercedes_benz_annual_report_2022.pdf
```

---

## Running the RAG System

From the project root:

```bash
python -m src.rag.main
```

The first run will:
1. Load all PDFs from `data/pdfs/`
2. Extract tables (via `tabula-py`) and chunk text (via LangChain's `RecursiveCharacterTextSplitter`)
3. Generate embeddings with `BAAI/bge-large-en-v1.5`
4. Persist everything to ChromaDB at `data/vector_store/`
5. Retrieve the top-10 most relevant chunks for the hardcoded demo query
6. Send them to the OpenAI LLM and print the answer

To query programmatically:

```python
from src.rag.main import initialize_rag_system, get_rag_response

rag_retriever = initialize_rag_system()
result = get_rag_response("What was the net profit in 2022?", rag_retriever)

print(result["answer"])   # LLM answer
print(result["source"])   # Pages cited
```

---

## Running Evaluations

Ensure your `.env` has valid LangSmith credentials, then:

```bash
python -m tests.evaluators
```

This will:
1. Run the RAG pipeline on every question in `data/dataset/dataset.xlsx`
2. Write LLM responses back into the spreadsheet
3. Upload the dataset to LangSmith
4. Run 4 LLM-based evaluators (correctness, relevance, groundedness, retrieval relevance)
5. Print the LangSmith experiment URL

---

## Configuration

Edit [config/config.py](config/config.py) to change core settings:

| Constant | Default | Description |
|---|---|---|
| `OPENAI_MODEL` | `"gpt-5.4"` | OpenAI model used for generation and evaluation |
| `DATA_DIR` | `"data/pdfs"` | Directory scanned for PDF input files |
| `DATASET_PATH` | `"data/dataset/dataset.xlsx"` | Evaluation dataset spreadsheet |

Retrieval parameters can be tuned directly in [src/rag/main.py](src/rag/main.py):

| Parameter | Default | Description |
|---|---|---|
| `top_k` | `10` | Number of chunks retrieved per query |
| `score_threshold` | `0.35` | Minimum cosine similarity to include a chunk |

Chunking parameters can be tuned in [src/rag/ingestion_pipeline.py](src/rag/ingestion_pipeline.py):

| Parameter | Default | Description |
|---|---|---|
| `chunk_size` | `1200` | Maximum characters per text chunk |
| `chunk_overlap` | `300` | Overlap between consecutive chunks |

---

## Re-ingesting Documents

The pipeline skips ingestion if the vector store is non-empty. To force a fresh ingest (e.g. after adding new PDFs), delete the vector store directory:

```bash
# Windows
rmdir /s /q data\vector_store

# macOS / Linux
rm -rf data/vector_store
```

Then re-run the system normally.
