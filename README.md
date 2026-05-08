# HMK — Offline Company AI Assistant

A fully offline voice-enabled AI assistant for the fictional company **Nova Finance**. Runs entirely on your Apple Silicon Mac. Built as a college final-year project.

- Local LLM via **Ollama** (`llama3.2:3b`)
- Speech-to-text via **mlx-whisper** (Metal-accelerated on M-series)
- Text-to-speech via **kokoro-onnx**
- RAG over a single `data/company.txt` using **sentence-transformers** + numpy
- FastAPI backend, single-page Tailwind frontend with browser `MediaRecorder`
- No cloud calls anywhere after the one-time model downloads

## Prerequisites

- macOS on Apple Silicon (M1/M2/M3)
- Python 3.10+
- [Homebrew](https://brew.sh)

## One-time Setup

```bash
# 1. Install Ollama and ffmpeg
brew install ollama ffmpeg

# 2. Start the Ollama daemon (leave running in another terminal/tab)
ollama serve

# 3. Pull the LLM (~2 GB)
ollama pull llama3.2:3b

# 4. Clone / cd into the project
cd /Users/macos/Desktop/repos/HMK

# 5. Create venv and install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The first run will additionally auto-download:

- Whisper weights (~480 MB) into `~/.cache/huggingface/`
- Embedding model `all-MiniLM-L6-v2` (~90 MB) into `~/.cache/huggingface/`
- Kokoro TTS model + voices (~340 MB) into `models/`

After that, the app works fully offline.

## Run

```bash
source .venv/bin/activate
uvicorn app.main:app --host localhost --port 8000
```

Open **http://localhost:8000** in Chrome (or Safari).

> Use `localhost`, not `127.0.0.1` — Safari mic permissions are stricter on the latter.

The first startup takes ~30–60 seconds (model warmups). Subsequent starts are faster.

## Demo Script (for college presentation)

Try these prompts to show off RAG, voice, and grounded answers:

1. **Org chart** — *"Who is the CFO of Nova Finance?"* → "Rohan Desai"
2. **Team-specific** — *"I'm joining the finance team. Who will be my manager for the first 30 days?"* → "Rahul Khanna"
3. **Policy** — *"What's the work from home policy?"* → 3 days office, 2 days WFH
4. **Onboarding** — *"What do I need to do on my first day?"* → laptop pickup, IT setup, welcome session, etc.
5. **Voice** — Click the mic and ask any of the above out loud
6. **Grounding** — *"What's the weather in Tokyo?"* → assistant declines, proving it doesn't hallucinate
7. **Memory** — *"Who's the CEO?"* then *"And who reports to them?"* → uses prior turn

## Project Layout

```
HMK/
├── app/
│   ├── main.py        # FastAPI app, startup warmup, static mount
│   ├── routes.py      # /api/chat, /api/voice, /api/reset
│   ├── llm.py         # Ollama wrapper, prompt template, history
│   ├── rag.py         # corpus split, embed, retrieve
│   ├── stt.py         # mlx-whisper transcription
│   ├── tts.py         # kokoro-onnx synthesis (auto-downloads model)
│   ├── audio.py       # ffmpeg webm/mp4 -> wav
│   └── config.py      # paths and constants
├── static/
│   ├── index.html     # Tailwind + glassy chat UI
│   └── app.js         # MediaRecorder + chat state
├── data/
│   ├── company.txt    # Nova Finance handbook (made-up)
│   └── embeddings.npz # cached embeddings (auto-generated, gitignored)
├── models/            # Kokoro model files (auto-downloaded, gitignored)
├── requirements.txt
└── README.md
```

## Architecture

```
Browser  ─ webm audio ─►  FastAPI  ─►  ffmpeg  ─►  WAV (16k mono)
                                                      │
                                          mlx-whisper STT
                                                      │ text
                                          numpy cosine RAG over
                                          MiniLM embeddings of company.txt
                                                      │ top-k chunks + history
                                          Ollama (llama3.2:3b)
                                                      │ reply
                                          kokoro-onnx TTS
                                                      │
Browser ◄─ JSON { transcript, reply, audio_b64 } ◄────┘
```

## Troubleshooting

- **`ollama` connection refused** — `ollama serve` is not running. Start it in another terminal.
- **`ffmpeg not found`** — `brew install ffmpeg`.
- **Mic permission denied** — Ensure you opened the page on `http://localhost:8000` (not `127.0.0.1`). Grant mic access in browser settings.
- **First reply is slow** — Cold model load. Subsequent replies are fast. Warmup happens at startup, but first inference is still slower than steady-state.
- **Out of memory** — Close other heavy apps. The 3B LLM + Whisper + embeddings + Kokoro needs ~6 GB. On 8 GB Macs, quit Chrome tabs.
- **Kokoro download fails** — Manually download the two files into `models/`:
  - https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
  - https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

## License

MIT (this repo). Models and data have their own licenses — check before redistributing.
