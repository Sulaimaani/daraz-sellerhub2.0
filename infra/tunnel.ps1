# Cloudflared Native Setup Script for Windows
# Run this in PowerShell to start a temporary tunnel to your local backend

$URL = "http://localhost:8000"

Write-Host "Checking for cloudflared..." -ForegroundColor Cyan

if (-not (Get-Command "cloudflared" -ErrorAction SilentlyContinue)) {
    Write-Host "cloudflared not found in PATH." -ForegroundColor Yellow
    Write-Host "Downloading cloudflared.exe..." -ForegroundColor Cyan
    $DownloadUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    $DestPath = "$env:TEMP\cloudflared.exe"
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $DestPath
    
    Write-Host "Running temporary cloudflared tunnel..." -ForegroundColor Green
    & $DestPath tunnel --url $URL
} else {
    Write-Host "cloudflared is installed. Running tunnel..." -ForegroundColor Green
    cloudflared tunnel --url $URL
}
