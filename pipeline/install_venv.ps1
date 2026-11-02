# pipeline/install_venv.ps1 — create .venv (Python 3.11) and install the pinned audio/ML stack.
# Re-runnable. Log: logs/install_venv.log
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot     # C:\channel
New-Item -ItemType Directory -Force -Path "$root\logs" | Out-Null
Start-Transcript -Path "$root\logs\install_venv.log" -Force

$py = "$root\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    py -3.11 -m venv "$root\.venv"
}

& $py -m pip install --upgrade pip
# CPU-only torch first (smaller than CUDA build; GPU is an optional later step)
& $py -m pip install torch --index-url https://download.pytorch.org/whl/cpu
# stack: TTS, ASR, analysis, tooling. espeakng-loader ships espeak-ng for Kokoro on Windows.
& $py -m pip install kokoro soundfile faster-whisper numpy scipy librosa pyloudnorm jsonschema pillow espeakng-loader

# record exact versions for reproducibility
& $py -m pip freeze > "$root\requirements.txt"

Stop-Transcript
Write-Output "VENV INSTALL DONE"
