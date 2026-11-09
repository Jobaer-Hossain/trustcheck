"""
TrustCheck FastAPI Server
Exposes audio forensics analysis endpoints and serves the real-time meeting shield dashboard.
"""

from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from trustcheck.core.detector import DeepfakeDetector
from trustcheck.core.models import VoiceTrustReport

app = FastAPI(
    title="TrustCheck API",
    description="Multi-Modal Deepfake & Voice Phishing Shield",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/status")
def get_status():
    return {
        "status": "online",
        "shield": "TrustCheck Acoustic DSP Detector",
        "version": "1.0.0"
    }


@app.post("/api/analyze/upload", response_model=VoiceTrustReport)
async def analyze_uploaded_audio(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    if len(audio_bytes) < 100:
        raise HTTPException(status_code=400, detail="Invalid audio file size")
    return DeepfakeDetector.evaluate_audio(audio_bytes, file_name=file.filename)


@app.get("/api/analyze/demo/{sample_type}", response_model=VoiceTrustReport)
def run_demo_sample(sample_type: str):
    """Generates synthetic vs authentic test samples for interactive demonstration."""
    import math
    import struct

    rate = 16000
    duration_secs = 2.0
    n = int(rate * duration_secs)

    if sample_type == "authentic":
        # Simulates natural human speech: fundamental ~140Hz with natural micro-jitter and harmonic decay
        samples = []
        for i in range(n):
            jitter = math.sin(i * 0.005) * 0.008  # natural 0.8% micro-jitter
            freq = 140.0 * (1.0 + jitter)
            # Fund + Formants
            val = (
                0.5 * math.sin(2 * math.pi * freq * (i / rate)) +
                0.25 * math.sin(2 * math.pi * (freq * 2) * (i / rate)) +
                0.12 * math.sin(2 * math.pi * (freq * 3) * (i / rate))
            )
            samples.append(val)
        file_name = "authentic_human_caller.wav"
    else:
        # Simulates AI voice clone: zero jitter (quantized pitch) + high frequency flat noise
        samples = []
        for i in range(n):
            freq = 155.0  # perfectly flat pitch
            val = 0.6 * math.sin(2 * math.pi * freq * (i / rate)) + (0.05 * math.sin(i * 0.9))
            samples.append(val)
        file_name = "synthetic_ai_voice_clone.wav"

    # Encode as WAV
    pcm = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples)
    header = (
        b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVE" +
        b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, rate, rate * 2, 2, 16) +
        b"data" + struct.pack("<I", len(pcm))
    )
    wav_bytes = header + pcm

    return DeepfakeDetector.evaluate_audio(wav_bytes, file_name=file_name)


# Mount Web Dashboard
static_path = Path(__file__).resolve().parent.parent / "web" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def serve_index():
    index_file = static_path / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>TrustCheck Deepfake Shield</h1>")
