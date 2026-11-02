# pipeline/bootstrap_ffmpeg.ps1 — download portable ffmpeg+ffprobe into C:\channel\tools\ffmpeg.
# No admin, no winget. Re-runnable. Log: logs/install_ffmpeg.log
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
New-Item -ItemType Directory -Force -Path "$root\logs", "$root\tools" | Out-Null
Start-Transcript -Path "$root\logs\install_ffmpeg.log" -Force

$zip = "$root\tools\ffmpeg-release-essentials.zip"
$dst = "$root\tools"
if (-not (Test-Path "$dst\ffmpeg\bin\ffmpeg.exe")) {
    if (-not (Test-Path $zip)) {
        $ProgressPreference = "SilentlyContinue"
        Invoke-WebRequest -Uri "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" -OutFile $zip -UseBasicParsing
    }
    if (Test-Path "$dst\ffmpeg") { Remove-Item -Recurse -Force "$dst\ffmpeg" }
    Expand-Archive -LiteralPath $zip -DestinationPath "$dst\ffmpeg_tmp" -Force
    $bin = Get-ChildItem "$dst\ffmpeg_tmp" -Directory | Select-Object -First 1
    Move-Item $bin.FullName "$dst\ffmpeg"
    Remove-Item -Recurse -Force "$dst\ffmpeg_tmp"
    Remove-Item $zip -Force
}
& "$dst\ffmpeg\bin\ffmpeg.exe" -version | Select-Object -First 1
& "$dst\ffmpeg\bin\ffprobe.exe" -version | Select-Object -First 1

# register for every future terminal (user scope, no admin)
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (($userPath -split ";") -notcontains "$dst\ffmpeg\bin") {
    [Environment]::SetEnvironmentVariable("Path", ($userPath.TrimEnd(";") + ";" + "$dst\ffmpeg\bin"), "User")
}
[Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User")
[Environment]::SetEnvironmentVariable("HF_HOME", "$root\cache\hf", "User")

Stop-Transcript
Write-Output "FFMPEG BOOTSTRAP DONE"
