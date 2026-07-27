import os
import tempfile

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# -------------------------------------------------------
# Chroma Configuration
# -------------------------------------------------------

COLLECTION_NAME = "meeting_transcript"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Streamlit Cloud compatible writable directory
CHROMA_DIR = os.path.join(tempfile.gettempdir(), "meetmind_vector_db")


# -------------------------------------------------------
# Embedding Model
# -------------------------------------------------------

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )


# -------------------------------------------------------
# Build Vector Store
# -------------------------------------------------------

def build_vector_store(transcript: str) -> Chroma:

    if not transcript or transcript.strip() == "":
        raise ValueError("Transcript is empty.")

    print("Building vector store...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = splitter.split_text(transcript)

    docs = [
        Document(
            page_content=chunk,
            metadata={"chunk_index": i},
        )
        for i, chunk in enumerate(chunks)
    ]

    embeddings = get_embeddings()

    # Remove previous temporary DB
    if os.path.exists(CHROMA_DIR):
        import shutil
        shutil.rmtree(CHROMA_DIR, ignore_errors=True)

    os.makedirs(CHROMA_DIR, exist_ok=True)

    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR,
    )

    print(f"✅ Vector store created with {len(docs)} chunks.")

    return vector_store


# -------------------------------------------------------
# Load Existing Vector Store
# -------------------------------------------------------

def load_vector_store() -> Chroma:

    embeddings = get_embeddings()

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )


# -------------------------------------------------------
# Retriever
# -------------------------------------------------------

def get_retriever(
    vector_store: Chroma,
    k: int = 4,
):

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )