import os
import tabula

processed_tables_directory = "data/processed_data/processed_tables"
processed_text_directory = "data/processed_data/processed_text"

# Create directories if they don't exist
os.makedirs(processed_tables_directory, exist_ok=True)
os.makedirs(processed_text_directory, exist_ok=True)


def process_tables(doc, items, filepath):
    """
    Extract tables from a single document page
    and save them as text files.
    """

    page_num = doc.metadata.get("page", 0)

    try:
        tables = tabula.read_pdf(
            filepath,
            pages=page_num + 1,
            multiple_tables=True
        )

        if not tables:
            return

        for table_idx, table in enumerate(tables):

            # Replace NaN values with empty strings
            table = table.fillna("")

            # Convert dataframe rows into pipe-separated text
            table_text = "\n".join(
                [
                    " | ".join(map(str, row))
                    for row in table.values
                ]
            )

            table_file_name = os.path.join(
                processed_tables_directory,
                f"{os.path.basename(filepath)}_table_{page_num}_{table_idx}.txt"
            )

            # Save extracted table text
            with open(
                table_file_name,
                "w",
                encoding="utf-8",
                errors="ignore"
            ) as f:
                f.write(table_text)

            items.append({
                "page": page_num,
                "type": "table",
                "text": table_text,
                "path": table_file_name
            })

    except Exception as e:
        print(f"Error extracting tables from page {page_num}: {str(e)}")


def split_documents(doc, text_splitter, items, filepath):
    """
    Split a single document into chunks
    and save them as text files.
    """

    page_num = doc.metadata.get("page", 0)

    chunks = text_splitter.split_documents([doc])

    for chunk_idx, chunk in enumerate(chunks):

        text_file_name = os.path.join(
            processed_text_directory,
            f"{os.path.basename(filepath)}_text_{page_num}_{chunk_idx}.txt"
        )

        # Save chunk text
        with open(
            text_file_name,
            "w",
            encoding="utf-8",
            errors="ignore"
        ) as f:
            f.write(chunk.page_content)

        items.append({
            "page": page_num,
            "type": "text",
            "text": chunk.page_content,
            "path": text_file_name
        })

    return chunks