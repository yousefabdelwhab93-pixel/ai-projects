
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


from project1_rag.config import (
    DATA_DIR,
    DB_DIR,
    COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBED_MODEL,
)


def load_documents():
    """Load all PDF and TXT files from the data directory."""
    documents = []

    for file_path in DATA_DIR.iterdir():
        if file_path.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(file_path))
            documents.extend(loader.load())

        elif file_path.suffix.lower() == ".txt":
            loader = TextLoader(str(file_path), encoding="utf-8")
            documents.extend(loader.load())

    return documents


def split_documents(documents):
    """Split documents into smaller chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    return splitter.split_documents(documents)


def build_vector_store(chunks):
    """Rebuild the Chroma vector database from scratch."""

    # Remove the previous database to avoid duplicate chunks
    if DB_DIR.exists():
        import shutil
        shutil.rmtree(DB_DIR)

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_DIR),
    )

    return vector_store


if __name__ == "__main__":
    if not DATA_DIR.exists():
        print(f"Data directory not found: {DATA_DIR}")

    else:
        documents = load_documents()

        if not documents:
            print("No PDF or TXT documents found in data/.")

        else:
            chunks = split_documents(documents)

            build_vector_store(chunks)

            source_files = {
                doc.metadata.get("source", "Unknown")
                for doc in documents
            }

            print(
                f"{len(source_files)} files -> "
                f"{len(chunks)} chunks"
            )
            print(f"Vector database created at: {DB_DIR}")
