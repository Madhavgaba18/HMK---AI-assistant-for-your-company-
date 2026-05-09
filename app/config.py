from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"
STATIC_DIR = ROOT / "static"

CORPUS_PATH = DATA_DIR / "company.txt"
EMBEDDINGS_CACHE = DATA_DIR / "embeddings.npz"

LLM_MODEL = "llama3.2:3b"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
WHISPER_MODEL = "mlx-community/whisper-small-mlx"

KOKORO_MODEL = MODELS_DIR / "kokoro-v1.0.onnx"
KOKORO_VOICES = MODELS_DIR / "voices-v1.0.bin"
KOKORO_VOICE = "af_sarah"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 60
TOP_K = 4
HISTORY_TURNS = 6

RAG_THRESHOLD = 0.40
GENERAL_REPLY_PREFIX = "(General knowledge — not from Nova Finance docs)\n\n"
