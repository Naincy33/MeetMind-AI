import os
import whisper

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")

_model = None


def load_model():
    global _model

    if _model is None:
        print(f"Loading Whisper model: {WHISPER_MODEL}...")
        _model = whisper.load_model(WHISPER_MODEL)
        print("Whisper model loaded.")

    return _model


def transcribe_chunk(chunk_path: str) -> str:
    """
    Transcribe one audio chunk using Whisper.
    """

    model = load_model()

    result = model.transcribe(
        chunk_path,
        task="transcribe",
        fp16=False,   # Required for CPU
    )

    return result["text"]


def transcribe_all(chunks: list[str]) -> str:
    """
    Transcribe all chunks and return one transcript.
    """

    print("Using Whisper for transcription.")

    transcript = []

    total = len(chunks)

    for i, chunk in enumerate(chunks, start=1):
        print(f"Transcribing chunk {i}/{total}...")
        transcript.append(transcribe_chunk(chunk))

    print("Transcription complete.")

    return "\n".join(transcript)