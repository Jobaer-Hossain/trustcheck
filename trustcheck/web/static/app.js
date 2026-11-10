/**
 * TrustCheck Frontend Logic
 * Oscilloscope rendering, mic audio recording, and deepfake verification.
 */

let canvas, ctx;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();
  initCanvas();
  drawDefaultWaveform();

  // Demo buttons
  document.getElementById("btn-demo-authentic").onclick = () => loadDemoSample("authentic");
  document.getElementById("btn-demo-deepfake").onclick = () => loadDemoSample("deepfake");

  // File upload
  document.getElementById("file-upload").onchange = (e) => {
    const file = e.target.files[0];
    if (file) uploadAudioFile(file);
  };

  // Mic recording
  document.getElementById("btn-record-mic").onclick = toggleMicRecording;

  // Load initial demo
  loadDemoSample("authentic");
});

function initCanvas() {
  canvas = document.getElementById("waveform-canvas");
  ctx = canvas.getContext("2d");
  canvas.width = canvas.parentElement.clientWidth;
  canvas.height = canvas.parentElement.clientHeight;
}

function drawWaveform(jitterRatio = 0.8, isAI = false) {
  if (!ctx) return;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.lineWidth = 2.5;
  ctx.strokeStyle = isAI ? "#f43f5e" : "#10b981";
  ctx.beginPath();

  const sliceWidth = canvas.width / 200;
  let x = 0;

  for (let i = 0; i < 200; i++) {
    const jitter = isAI ? 0 : (Math.random() - 0.5) * 0.25;
    const v = Math.sin(i * 0.15) * 0.4 + jitter;
    const y = (v * canvas.height / 2) + (canvas.height / 2);

    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);

    x += sliceWidth;
  }
  ctx.stroke();
}

function drawDefaultWaveform() {
  drawWaveform(0.8, false);
}

async function loadDemoSample(type) {
  try {
    const res = await fetch(`/api/analyze/demo/${type}`);
    const report = await res.json();
    renderReport(report);
    drawWaveform(report.acoustic_features.pitch_jitter_pct, type === "deepfake");
  } catch (err) {
    console.error("Demo load error:", err);
  }
}

async function uploadAudioFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/analyze/upload", {
      method: "POST",
      body: formData
    });
    const report = await res.json();
    renderReport(report);
    drawWaveform(report.acoustic_features.pitch_jitter_pct, report.trust_score_pct < 70);
  } catch (err) {
    console.error("Upload error:", err);
  }
}

function renderReport(report) {
  document.getElementById("trust-score-val").innerText = report.trust_score_pct.toFixed(1);
  const scoreValEl = document.getElementById("trust-score-val");
  const badgeEl = document.getElementById("verdict-badge");

  if (report.trust_score_pct >= 80) {
    scoreValEl.className = "text-5xl font-extrabold text-emerald-600";
    badgeEl.className = "mt-3 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 inline-block";
  } else if (report.trust_score_pct >= 50) {
    scoreValEl.className = "text-5xl font-extrabold text-amber-600";
    badgeEl.className = "mt-3 px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200 inline-block";
  } else {
    scoreValEl.className = "text-5xl font-extrabold text-rose-600";
    badgeEl.className = "mt-3 px-3 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200 inline-block";
  }

  badgeEl.innerText = report.verdict;
  document.getElementById("verdict-summary").innerText = report.summary_verdict;
  document.getElementById("audio-file-name").innerText = report.file_name;

  // Features
  const feat = report.acoustic_features;
  document.getElementById("stat-jitter").innerText = `${feat.pitch_jitter_pct.toFixed(2)}%`;
  document.getElementById("stat-flatness").innerText = feat.spectral_flatness.toFixed(3);
  document.getElementById("stat-centroid").innerText = `${Math.round(feat.spectral_centroid_hz)} Hz`;
  document.getElementById("stat-noise").innerText = `${feat.noise_floor_db.toFixed(1)} dB`;

  // Anomalies
  const container = document.getElementById("anomalies-container");
  const countBadge = document.getElementById("anomalies-count-badge");
  container.innerHTML = "";

  if (report.detected_anomalies.length === 0) {
    countBadge.innerText = "0 Anomalies Detected";
    countBadge.className = "px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200";
    container.innerHTML = `
      <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center text-xs text-emerald-700 font-medium">
        ✔ All biological speech metrics fall within normal human vocal cord parameters.
      </div>
    `;
  } else {
    countBadge.innerText = `${report.detected_anomalies.length} Anomalies Flagged`;
    countBadge.className = "px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-50 text-rose-700 border border-rose-200";

    report.detected_anomalies.forEach(a => {
      const card = document.createElement("div");
      card.className = "p-3.5 rounded-xl bg-rose-50/50 border border-rose-200 space-y-1.5 text-xs";
      card.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="font-bold text-rose-700">${a.feature_name}</span>
          <span class="text-slate-500 font-mono text-[11px]">Observed: ${a.observed_value} (Normal: ${a.expected_human_range})</span>
        </div>
        <p class="text-slate-700 leading-relaxed">${a.explanation}</p>
      `;
      container.appendChild(card);
    });
  }

  lucide.createIcons();
}

async function toggleMicRecording() {
  const btnText = document.getElementById("record-btn-text");

  if (!isRecording) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
        const file = new File([audioBlob], "live_mic_capture.wav", { type: "audio/wav" });
        uploadAudioFile(file);
      };

      mediaRecorder.start();
      isRecording = true;
      btnText.innerText = "Stop Recording...";
    } catch (err) {
      alert("Microphone access denied or unavailable.");
    }
  } else {
    mediaRecorder.stop();
    isRecording = false;
    btnText.innerText = "Record Microphone";
  }
}
