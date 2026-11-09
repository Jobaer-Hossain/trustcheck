"""
TrustCheck Data Models
Schemas for acoustic features, DSP forensic metrics, and deepfake trust verdicts.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class TrustVerdict(str, Enum):
    AUTHENTIC_HUMAN = "Authentic Human Voice"
    SUSPICIOUS_SYNTHESIS = "Suspicious / Potential Voice Clone"
    HIGH_CONFIDENCE_DEEPFAKE = "High Confidence Synthetic Deepfake"


class AcousticFeatures(BaseModel):
    duration_seconds: float
    sample_rate: int
    zero_crossing_rate_mean: float
    zero_crossing_rate_std: float
    spectral_centroid_hz: float
    spectral_flatness: float
    pitch_jitter_pct: float = Field(..., description="Vocal cord micro-frequency instability (natural speech is 0.5% - 1.5%)")
    shimmer_db: float = Field(..., description="Vocal amplitude micro-fluctuation")
    noise_floor_db: float
    high_freq_harmonic_ratio: float


class ForensicAnomaly(BaseModel):
    feature_name: str
    observed_value: str
    expected_human_range: str
    risk_level: str  # "high", "medium", "low"
    explanation: str


class VoiceTrustReport(BaseModel):
    analyzed_at: datetime = Field(default_factory=datetime.now)
    file_name: str
    trust_score_pct: float = Field(..., description="0-100% score (100% = fully authentic human)")
    verdict: TrustVerdict
    risk_badge_color: str
    acoustic_features: AcousticFeatures
    detected_anomalies: List[ForensicAnomaly]
    summary_verdict: str
