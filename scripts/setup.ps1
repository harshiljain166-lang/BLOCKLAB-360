$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
Set-Location backend
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\pip.exe install -r requirements.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue
Set-Location ..\frontend
npm install
Write-Host 'Setup complete. Run scripts/run-dev.ps1 in a new PowerShell window.'
