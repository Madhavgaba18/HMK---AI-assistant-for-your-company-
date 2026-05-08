from __future__ import annotations

import io
import re
import urllib.request

import soundfile as sf
from kokoro_onnx import Kokoro

from . import config


_MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
_VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

_kokoro: Kokoro | None = None


def _ensure_files() -> None:
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for path, url in [
        (config.KOKORO_MODEL, _MODEL_URL),
        (config.KOKORO_VOICES, _VOICES_URL),
    ]:
        if not path.exists():
            print(f"[tts] downloading {path.name} ({url}) ...")
            urllib.request.urlretrieve(url, path)


def load() -> None:
    global _kokoro
    _ensure_files()
    _kokoro = Kokoro(str(config.KOKORO_MODEL), str(config.KOKORO_VOICES))


def _strip_for_speech(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[\*\-•]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[`*#]", "", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def synthesize(text: str) -> bytes:
    if _kokoro is None:
        raise RuntimeError("tts.load() must be called before synthesize()")
    samples, sample_rate = _kokoro.create(
        _strip_for_speech(text), voice=config.KOKORO_VOICE, speed=1.0, lang="en-us"
    )
    buf = io.BytesIO()
    sf.write(buf, samples, sample_rate, format="WAV")
    return buf.getvalue()
