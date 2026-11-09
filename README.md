# TrustCheck

> **Multi-modal deepfake and voice phishing shield.**  
> Real-time acoustic digital signal processing (DSP) for detecting neural vocoder artifacts and synthetic voice clones.

With the proliferation of zero-shot neural voice cloning tools (like Tortoise, XTTS, and ElevenLabs), voice phishing and CEO fraud have become rampant threats in finance, enterprise communication, and customer verification.

TrustCheck analyzes incoming voice streams and audio recordings using signal processing heuristics based on biological vocal tract physiology:
* **Pitch Micro-Jitter**: Natural human vocal cords vibrate with $0.45\% - 1.80\%$ cycle-to-cycle frequency micro-instability. Synthetic voices typically exhibit either rigid quantization ($< 0.25\%$) or erratic diffusion artifacts ($> 3.5\%$).
* **High-Frequency Spectral Flatness**: Neural vocoders (HiFi-GAN, MelGAN) introduce abnormal noise flatness in upper frequency bands.
* **Harmonic-to-Noise Ratio & Room Impulse Reverberation**: Cloned voices generated in isolation lack natural room acoustics and acoustic reverberation.

---

## Forensic Trust Verdicts

| Trust Score | Classification | Action |
|---|---|---|
| **$80\% - 100\%$** | **Authentic Human Voice** | Low risk; biological micro-instability and natural harmonics verified. |
| **$50\% - 79\%$** | **Suspicious / Potential Voice Clone** | Moderate risk; borderline acoustic anomalies or heavy compression. |
| **$< 50\%$** | **High Confidence Synthetic Deepfake** | High risk; algorithmic pitch invariance and vocoder synthesis detected. |

---

## Quickstart

### Installation
```bash
git clone https://github.com/Jobaer-Hossain/trustcheck.git
cd trustcheck

pip install -r requirements.txt
```

### CLI Audio Inspection
```bash
# Inspect any WAV or audio file
python -m trustcheck.cli inspect suspicious_caller.wav
```

### Web Console & Oscilloscope
```bash
python run.py --port 8004
```
Open **`http://localhost:8004`** to use the live acoustic oscilloscope, test with microphone recording, or run interactive authentic vs synthetic voice demos.

---

## REST API
* `POST /api/analyze/upload`: Upload an audio file for forensic verification.
* `GET /api/analyze/demo/authentic`: Run verification against authentic human baseline.
* `GET /api/analyze/demo/deepfake`: Run verification against synthetic vocoder clone.

---

## Automated Tests
```bash
python -m unittest tests.test_trustcheck
```

---

## License
MIT License. Free for open-source and commercial use.
