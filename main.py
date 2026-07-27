from dotenv import load_dotenv

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)
from core.rag_engine import build_rag_chain


# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# Main AI Pipeline
# --------------------------------------------------

def run_pipeline(source: str, language: str = "english") -> dict:
    """
    Complete AI Meeting Intelligence Pipeline

    Returns:
        dict containing:
        - title
        - transcript
        - summary
        - action_items
        - key_decisions
        - open_questions
        - rag_chain
    """

    print("\n==============================")
    print("Starting AI Video Assistant")
    print("==============================\n")

    # -----------------------------
    # Audio Processing
    # -----------------------------

    chunks = process_input(source)

    if not chunks:
        raise RuntimeError("No audio chunks were generated.")

    # -----------------------------
    # Speech to Text
    # -----------------------------

    transcript = transcribe_all(chunks, language)

    if not transcript.strip():
        raise RuntimeError("Transcription failed.")

    print("\nTranscript Preview\n")
    print(transcript[:300])
    print("\n------------------------------\n")

    # -----------------------------
    # AI Processing
    # -----------------------------

    title = generate_title(transcript)

    summary = summarize(transcript)

    action_items = extract_action_items(transcript)

    key_decisions = extract_key_decisions(transcript)

    open_questions = extract_questions(transcript)

    # -----------------------------
    # Build RAG
    # -----------------------------

    rag_chain = build_rag_chain(transcript)

    print("Pipeline Completed Successfully.\n")

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": key_decisions,
        "open_questions": open_questions,
        "rag_chain": rag_chain,
    }


# --------------------------------------------------
# CLI Mode
# --------------------------------------------------

if __name__ == "__main__":

    source = input(
        "Enter YouTube URL or Local File Path:\n> "
    ).strip()

    language = (
        input(
            "Language (english / hinglish):\n> "
        ).strip()
        or "english"
    )

    try:

        result = run_pipeline(source, language)

        print("\n" + "=" * 70)
        print(f"Meeting Title:\n{result['title']}")
        print("=" * 70)

        print("\nExecutive Summary\n")
        print(result["summary"])

        print("\nAction Items\n")
        print(result["action_items"])

        print("\nKey Decisions\n")
        print(result["key_decisions"])

        print("\nOpen Questions\n")
        print(result["open_questions"])

        print("\n" + "=" * 70)

    except Exception as e:

        print(f"\nPipeline Failed\n{e}")
        exit()

    # -----------------------------
    # RAG Chat
    # -----------------------------

    print("\nChat with your Meeting")
    print("Type 'exit' to quit.\n")

    rag_chain = result["rag_chain"]

    while True:

        question = input("You: ").strip()

        if question.lower() in ["exit", "quit", "q"]:
            print("\nGoodbye!")
            break

        if not question:
            continue

        try:

            from core.rag_engine import ask_question

            answer = ask_question(
                rag_chain,
                question,
            )

            print(f"\nAssistant:\n{answer}\n")

        except Exception as e:

            print(f"\nError:\n{e}\n")