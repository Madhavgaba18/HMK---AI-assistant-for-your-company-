"""LFM2 audio-to-audio bridge (Liquid Foundation Model v2)."""
from __future__ import annotations

from pathlib import Path

from . import config

_MODEL_ID = "LiquidAI/LFM2-Audio-1.5B"
_model = None


def load() -> None:
    global _model
    from transformers import AutoModelForCausalLM, AutoProcessor

    processor = AutoProcessor.from_pretrained(_MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(_MODEL_ID, torch_dtype="auto")
    _model = (processor, model)


def generate(wav_path: Path, session_id: str = "default") -> bytes:
    if _model is None:
        raise RuntimeError("lfm2.load() must be called before generate()")
    processor, model = _model
    inputs = processor(audio=str(wav_path), return_tensors="pt", sampling_rate=16000)
    output = model.generate(**inputs, max_new_tokens=512, do_sample=False)
    return processor.decode_audio(output[0])
