# Pins every Chromium renderer binary used by the pipeline onto the dedicated NVIDIA GPU.
# Windows default = power-saving integrated GPU; this writes GpuPreference=2 ("High performance")
# per exe, identical to Settings > System > Display > Graphics > High performance.
#
# Run again after: npm install/reinstall of remotion, or a playwright browser version bump.
# Verify during a render: nvidia-smi (RTX processes listed) or Task Manager > Performance > GPU.

$reg = "HKCU:\Software\Microsoft\DirectX\UserGpuPreferences"
if (-not (Test-Path $reg)) { New-Item -Path $reg -Force | Out-Null }

$targets = @()

# 1. Remotion's Chrome Headless Shell (lives inside remotion/node_modules/.remotion)
$targets += Get-ChildItem "C:\channel\remotion\node_modules\.remotion" -Recurse -Force `
  -Filter "chrome-headless-shell.exe" -ErrorAction SilentlyContinue

# 2. Playwright (2D studio kit): headless shell + full chromium, any installed version
$pw = "$env:LOCALAPPDATA\ms-playwright"
if (Test-Path $pw) {
  $targets += Get-ChildItem $pw -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -in @("chrome.exe", "headless_shell.exe") -and $_.FullName -match "chromium" }
}

if ($targets.Count -eq 0) { Write-Warning "no chromium renderer binaries found"; exit 1 }

foreach ($t in $targets | Select-Object -ExpandProperty FullName -Unique) {
  New-ItemProperty -Path $reg -Name $t -Value "GpuPreference=2;" -PropertyType String -Force | Out-Null
  Write-Host "pinned to dGPU: $t"
}

Write-Host "done - $($targets.Count) binary(ies) pinned."
