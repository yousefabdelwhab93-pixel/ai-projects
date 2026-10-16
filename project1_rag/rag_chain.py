
import os

from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate

from project1_rag.config import (
    DB_DIR,
    COLLECTION_NAME,
    TOP_K,
    CHAT_MODEL,
    EMBED_MODEL,
)


load_dotenv(find_dotenv())

PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a helpful assistant that answers questions using
ONLY the provided context.

If the answer is not supported by the context, respond exactly:
"I don't know from the provided documents."

Do not use outside knowledge.
Include citations to the source file and page when available."""
    ),
    (
        "human",
        "Context:\n{context}\n\nQuestion:\n{question}"
    ),
])


def format_docs(docs):
    """Format retrieved chunks with their source and page."""
    formatted_docs = []

    for doc in docs:
        source = os.path.basename(
            doc.metadata.get("source", "Unknown")
        )

        page = doc.metadata.get("page")
        page_info = f", p. {page + 1}" if page is not None else ""

        formatted_docs.append(
            f"[{source}{page_info}]\n{doc.page_content}"
        )

    return "\n\n".join(formatted_docs)


def get_retriever(search_type="mmr"):
    """Open Chroma and return an MMR or similarity retriever."""

    if not DB_DIR.exists():
        raise FileNotFoundError(
            "Chroma database not found. Run: "
            "python -m project1_rag.ingest"
        )

    if search_type not in ("mmr", "similarity"):
        raise ValueError(
            "search_type must be 'mmr' or 'similarity'"
        )

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL
    )

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_DIR),
        embedding_function=embeddings,
    )

    return vector_store.as_retriever(
        search_type=search_type,
        search_kwargs={"k": TOP_K},
    )


def build_rag_chain(search_type="mmr"):
    """Build a RAG function returning the question, docs, and answer."""

    retriever = get_retriever(search_type)

    llm = ChatOpenAI(
        model=CHAT_MODEL,
        api_key=os.getenv("INCEPTION_API_KEY"),
        base_url=os.getenv("INCEPTION_BASE_URL"),
        temperature=0,
    )

    chain = PROMPT | llm

    def answer_question(question):
        docs = retriever.invoke(question)

        if not docs:
            answer = "I don't know from the provided documents."
        else:
            response = chain.invoke({
                "context": format_docs(docs),
                "question": question,
            })
            answer = response.content

        return {
            "question": question,
            "docs": docs,
            "answer": answer,
        }

    return answer_question
