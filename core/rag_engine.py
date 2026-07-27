import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_mistralai import ChatMistralAI

from core.vector_store import (
    build_vector_store,
    load_vector_store,
    get_retriever,
)


# --------------------------------------------------
# LLM
# --------------------------------------------------

def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.2,
    )


# --------------------------------------------------
# Helper
# --------------------------------------------------

def format_docs(docs):
    if not docs:
        return "No transcript context available."

    return "\n\n".join(doc.page_content for doc in docs)


# --------------------------------------------------
# Prompt
# --------------------------------------------------

SYSTEM_PROMPT = """
You are an AI Meeting Assistant.

You MUST answer ONLY using the transcript context.

Rules:

1. Never use outside knowledge.
2. Never make up information.
3. If the answer is not clearly present in the transcript, reply EXACTLY:

"I could not find this information in the meeting transcript."

4. Keep answers concise.
5. Use bullet points whenever appropriate.
6. Do not mention information that is not in the transcript.

Transcript Context:

{context}
"""


# --------------------------------------------------
# Build New RAG
# --------------------------------------------------

def build_rag_chain(transcript: str):

    vector_store = build_vector_store(transcript)

    retriever = get_retriever(vector_store, k=4)

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{question}"),
        ]
    )

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


# --------------------------------------------------
# Load Existing RAG
# --------------------------------------------------

def load_rag_chain():

    vector_store = load_vector_store()

    retriever = get_retriever(vector_store)

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{question}"),
        ]
    )

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


# --------------------------------------------------
# Ask Question
# --------------------------------------------------

def ask_question(rag_chain, question: str) -> str:

    question = question.strip()

    if not question:
        return "Please enter a question."

    print(f"\nQuestion: {question}")

    answer = rag_chain.invoke(question)

    print(f"Answer: {answer}\n")

    return answer