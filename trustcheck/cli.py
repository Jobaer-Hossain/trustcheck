"""
TrustCheck CLI
Command-line acoustic deepfake and voice clone inspector.
"""

import sys
import io
import argparse
from pathlib import Path

# Windows UTF-8
if sys.platform == "win32":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from trustcheck.core.detector import DeepfakeDetector

console = Console(force_terminal=True)


def show_banner():
    console.print(
        Panel.fit(
            "[bold green]🛡️ TrustCheck[/bold green] — [bold white]Deepfake & Voice Phishing Shield[/bold white]\n"
            "[dim]Acoustic DSP Jitter & Spectral Forensics Inspector[/dim]",
            border_style="green"
        )
    )


def command_inspect(args):
    show_banner()
    file_path = Path(args.file).resolve()
    if not file_path.exists():
        console.print(f"[bold red]File not found:[/bold red] {file_path}")
        return

    audio_bytes = file_path.read_bytes()
    report = DeepfakeDetector.evaluate_audio(audio_bytes, file_name=file_path.name)

    badge_color = "green" if report.trust_score_pct >= 80 else ("yellow" if report.trust_score_pct >= 50 else "red")

    console.print(
        Panel(
            f"• [bold]File Inspected:[/bold] {report.file_name}\n"
            f"• [bold]Voice Authenticity Score:[/bold] [{badge_color} bold]{report.trust_score_pct}%[/{badge_color} bold]\n"
            f"• [bold]Verdict:[/bold] [{badge_color} bold]{report.verdict.value}[/{badge_color} bold]\n"
            f"• [bold]Summary:[/bold] {report.summary_verdict}",
            title="Voice Forensics Summary",
            border_style=badge_color
        )
    )

    # Features
    feat_table = Table(title="Acoustic Signal Features", header_style="bold cyan")
    feat_table.add_column("Forensic Metric")
    feat_table.add_column("Observed Value", style="bold yellow")
    feat_table.add_column("Expected Human Range", style="dim")

    feat = report.acoustic_features
    feat_table.add_row("Pitch Micro-Jitter", f"{feat.pitch_jitter_pct:.2f}%", "0.45% - 1.80%")
    feat_table.add_row("Spectral Flatness", f"{feat.spectral_flatness:.3f}", "0.050 - 0.350")
    feat_table.add_row("Spectral Centroid", f"{feat.spectral_centroid_hz:.1f} Hz", "Dynamic (300 - 4500 Hz)")
    feat_table.add_row("Noise Floor", f"{feat.noise_floor_db:.1f} dB", "< -30 dB")
    console.print(feat_table)

    if report.detected_anomalies:
        console.print("\n")
        anom_table = Table(title="Detected Forensic Anomalies", header_style="bold red")
        anom_table.add_column("Anomaly", style="bold red")
        anom_table.add_column("Observed", style="yellow")
        anom_table.add_column("Forensic Explanation")

        for a in report.detected_anomalies:
            anom_table.add_row(a.feature_name, a.observed_value, a.explanation)
        console.print(anom_table)
    else:
        console.print("\n[bold green]✔ Zero synthesis artifacts detected. Audio verified authentic.[/bold green]\n")


def main():
    parser = argparse.ArgumentParser(description="TrustCheck CLI")
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand")

    insp_p = subparsers.add_parser("inspect", help="Inspect an audio file for deepfake synthesis artifacts")
    insp_p.add_argument("file", help="Path to audio file (.wav)")

    args = parser.parse_args()
    if args.subcommand == "inspect":
        command_inspect(args)
    else:
        show_banner()
        parser.print_help()


if __name__ == "__main__":
    main()
