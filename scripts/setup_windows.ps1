Param(
  [switch]$Cuda = $false
)

$ErrorActionPreference = "Stop"

Write-Host ">>> Creating venv (.venv)"
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip wheel setuptools

Write-Host ">>> Installing requirements"
.\.venv\Scripts\pip install -r requirements.txt

if ($Cuda) {
  Write-Host ">>> Installing CUDA-enabled PyTorch (cu121)"
  .\.venv\Scripts\pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
} else {
  Write-Host ">>> (CPU or MPS) You can install CUDA PyTorch later if you have an NVIDIA GPU."
}

# ffmpeg check
$ff = (Get-Command ffmpeg -ErrorAction SilentlyContinue)
if (-not $ff) {
  Write-Warning "ffmpeg not found in PATH. Please install ffmpeg and add to PATH (e.g., via Chocolatey: choco install ffmpeg)."
} else {
  Write-Host "ffmpeg found: $($ff.Path)"
}

# Piper TTS check and installation
Write-Host ">>> Checking Piper TTS installation..."
$piper = (Get-Command piper -ErrorAction SilentlyContinue)
if (-not $piper) {
  Write-Warning "Piper TTS not found in PATH. Installing..."
  try {
    & "$PSScriptRoot\install_piper_windows.ps1"
  } catch {
    Write-Warning "Failed to install Piper automatically. Please run: .\scripts\install_piper_windows.ps1"
  }
} else {
  Write-Host "Piper TTS found: $($piper.Path)"
}

Write-Host ">>> Done. Activate venv with: .\.venv\Scripts\activate"
