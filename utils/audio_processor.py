import os
import subprocess
import yt_dlp

# Directory to store downloaded audio
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    """
    Download YouTube audio and convert it to WAV format.
    Returns the path of the downloaded WAV file.
    """
    output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        downloaded_file = ydl.prepare_filename(info)

    wav_file = os.path.splitext(downloaded_file)[0] + ".wav"
    return wav_file


def convert_to_wav(input_path: str) -> str:
    """
    Convert any supported audio/video file into mono 16kHz WAV for Whisper.
    Uses FFmpeg directly so pydub is not required.
    """
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-ac",
        "1",
        "-ar",
        "16000",
        output_path,
    ]

    subprocess.run(command, check=True)
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list[str]:
    """
    Split a WAV file into smaller chunks using FFmpeg.
    """
    duration_cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        wav_path,
    ]

    duration = float(subprocess.check_output(duration_cmd).decode().strip())
    chunk_seconds = chunk_minutes * 60

    chunks = []
    base_name = os.path.splitext(wav_path)[0]

    start = 0.0
    index = 0

    while start < duration:
        chunk_path = f"{base_name}_chunk_{index}.wav"
        command = [
            "ffmpeg",
            "-y",
            "-i",
            wav_path,
            "-ss",
            str(start),
            "-t",
            str(chunk_seconds),
            chunk_path,
        ]
        subprocess.run(command, check=True)
        chunks.append(chunk_path)
        start += chunk_seconds
        index += 1

    return chunks


def process_input(source: str) -> list[str]:
    """
    Process either a YouTube URL or a local file.

    Returns:
        List of chunked WAV files.
    """
    if source.startswith(("http://", "https://")):
        print("🎥 YouTube URL detected...")
        wav_path = download_youtube_audio(source)
    else:
        print("📁 Local file detected...")
        wav_path = convert_to_wav(source)

    print("✂️ Chunking audio...")
    chunks = chunk_audio(wav_path)

    print(f"✅ Audio ready! Created {len(chunks)} chunk(s).")
    return chunks


if __name__ == "__main__":
    source = input("Enter YouTube URL or local file path:\n")
    files = process_input(source)

    print("\nGenerated Files:")
    for file in files:
        print(file)