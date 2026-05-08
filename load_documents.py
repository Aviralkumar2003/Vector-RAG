from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader


# def load_pdf_documents(path: str):
#     dir_loader=DirectoryLoader(
#         path,
#         glob="**/*.pdf",
#         loader_cls=PyMuPDFLoader,
#         show_progress=False
#     )
#     return dir_loader.load()

def load_pdf_documents(path: str):

    all_documents=[]
    pdf_dir=Path(path)

    pdf_files=list(pdf_dir.glob("**/*.pdf"))
    print(f"Found {len(pdf_files)} PDF files in {path}")

    for pdf_file in pdf_files:
        print(f"Loading {pdf_file}...")

        try:
            loader=PyMuPDFLoader(str(pdf_file))
            documents=loader.load()

            for doc in documents:
                doc.metadata["source"]=pdf_file.name
                doc.metadata["file_type"]='pdf'

            all_documents.extend(documents)
            print(f"Loaded {len(documents)} documents from {pdf_file}")
        except Exception as e:
            print(f"Error loading {pdf_file}: {e}")
    print(f"Total loaded documents: {len(all_documents)}")
    return all_documents