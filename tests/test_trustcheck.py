"""
TrustCheck Automated Unit Tests
"""

import unittest
import math
import struct
from trustcheck.core.audio_dsp import AudioForensicDSP
from trustcheck.core.detector import DeepfakeDetector
from trustcheck.core.models import TrustVerdict


def make_dummy_wav(is_synthetic: bool = False) -> bytes:
    rate = 16000
    duration = 1.0
    n = int(rate * duration)
    samples = []

    for i in range(n):
        if is_synthetic:
            # Exactly 160 Hz -> exactly 100 samples per period (zero natural jitter) + vocoder noise
            val = 0.5 * math.sin(2 * math.pi * 160.0 * (i / rate)) + 0.1 * math.sin(i * 0.95)
        else:
            # Human micro-jitter ~0.8%
            jitter = math.sin(i * 0.01) * 0.008
            val = 0.5 * math.sin(2 * math.pi * 140.0 * (1.0 + jitter) * (i / rate))
        samples.append(val)

    pcm = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples)
    header = (
        b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVE" +
        b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, rate, rate * 2, 2, 16) +
        b"data" + struct.pack("<I", len(pcm))
    )
    return header + pcm


class TestTrustCheck(unittest.TestCase):

    def test_dsp_feature_extraction(self):
        wav = make_dummy_wav(is_synthetic=False)
        features = AudioForensicDSP.extract_features(wav)
        self.assertGreater(features.duration_seconds, 0.5)
        self.assertEqual(features.sample_rate, 16000)
        self.assertGreater(features.zero_crossing_rate_mean, 0.0)

    def test_authentic_speech_detection(self):
        wav = make_dummy_wav(is_synthetic=False)
        report = DeepfakeDetector.evaluate_audio(wav, "human_test.wav")
        self.assertGreaterEqual(report.trust_score_pct, 70.0)

    def test_synthetic_cloned_voice_detection(self):
        wav = make_dummy_wav(is_synthetic=True)
        report = DeepfakeDetector.evaluate_audio(wav, "synthetic_test.wav")
        # Should flag anomalies due to zero pitch micro-jitter
        self.assertLess(report.trust_score_pct, 80.0)
        self.assertGreater(len(report.detected_anomalies), 0)


if __name__ == "__main__":
    unittest.main()
