"""
TrustCheck Deepfake Classifier & Forensics Engine
Evaluates acoustic feature vectors against human biological speech baselines.
"""

from typing import List, Tuple
from trustcheck.core.models import (
    AcousticFeatures,
    ForensicAnomaly,
    VoiceTrustReport,
    TrustVerdict
)
from trustcheck.core.audio_dsp import AudioForensicDSP


class DeepfakeDetector:

    @classmethod
    def evaluate_audio(cls, audio_bytes: bytes, file_name: str = "sample.wav") -> VoiceTrustReport:
        features = AudioForensicDSP.extract_features(audio_bytes)
        anomalies: List[ForensicAnomaly] = []
        score = 100.0

        # Check 1: Pitch Jitter Instability
        if features.pitch_jitter_pct < 0.25:
            score -= 30.0
            anomalies.append(ForensicAnomaly(
                feature_name="Pitch Micro-Jitter",
                observed_value=f"{features.pitch_jitter_pct:.2f}%",
                expected_human_range="0.45% - 1.80%",
                risk_level="high",
                explanation="Robotic frequency invariance detected. Human vocal cords naturally vibrate with 0.5-1.5% micro-fluctuation; absence indicates algorithmic pitch quantization."
            ))
        elif features.pitch_jitter_pct > 3.8:
            score -= 25.0
            anomalies.append(ForensicAnomaly(
                feature_name="Pitch Micro-Jitter",
                observed_value=f"{features.pitch_jitter_pct:.2f}%",
                expected_human_range="0.45% - 1.80%",
                risk_level="high",
                explanation="Excessive phase jitter detected, typical of neural vocoder diffusion reconstruction artifacts."
            ))

        # Check 2: Spectral Flatness
        if features.spectral_flatness > 0.45:
            score -= 25.0
            anomalies.append(ForensicAnomaly(
                feature_name="High-Frequency Spectral Flatness",
                observed_value=f"{features.spectral_flatness:.3f}",
                expected_human_range="0.050 - 0.350",
                risk_level="high",
                explanation="Unnatural high-band noise distribution consistent with spectrogram-to-waveform vocoder synthesis (e.g. HiFi-GAN / MelGAN)."
            ))

        # Check 3: Zero-Crossing Rate
        if features.zero_crossing_rate_mean > 0.28:
            score -= 15.0
            anomalies.append(ForensicAnomaly(
                feature_name="Zero-Crossing Rate (ZCR)",
                observed_value=f"{features.zero_crossing_rate_mean:.3f}",
                expected_human_range="0.040 - 0.220",
                risk_level="medium",
                explanation="Elevated high-frequency zero-crossings indicating synthetic sibilance artifacts."
            ))

        # Normalize score
        final_score = max(5.0, min(99.0, score))

        if final_score >= 80.0:
            verdict = TrustVerdict.AUTHENTIC_HUMAN
            color = "emerald"
            summary = "Voice acoustic patterns match authentic human vocal tract physiology. Natural micro-jitter and harmonic distribution confirmed."
        elif final_score >= 50.0:
            verdict = TrustVerdict.SUSPICIOUS_SYNTHESIS
            color = "amber"
            summary = "Borderline acoustic anomalies detected. Potential voice clone, heavy audio compression, or digital speech processing filter."
        else:
            verdict = TrustVerdict.HIGH_CONFIDENCE_DEEPFAKE
            color = "rose"
            summary = "Critical neural vocoder synthesis artifacts identified. High probability of synthesized voice clone or deepfake audio."

        return VoiceTrustReport(
            file_name=file_name,
            trust_score_pct=round(final_score, 1),
            verdict=verdict,
            risk_badge_color=color,
            acoustic_features=features,
            detected_anomalies=anomalies,
            summary_verdict=summary
        )
