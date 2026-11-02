# pipeline/install_studio.ps1 — npm install for the vendored kit studio/ and the remotion/ project.
# Downloads: npm packages + Playwright Chromium + Remotion headless browser. Re-runnable.
# Log: logs/install_studio.log
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
New-Item -ItemType Directory -Force -Path "$root\logs" | Out-Null
Start-Transcript -Path "$root\logs\install_studio.log" -Force

# vendored kit (playwright, three, fonts)
Push-Location "$root\studio"
npm install
npx playwright install chromium
Pop-Location

# remotion composition project
Push-Location "$root\remotion"
npm install
npx remotion browser ensure
Pop-Location

Stop-Transcript
Write-Output "STUDIO + REMOTION INSTALL DONE"
