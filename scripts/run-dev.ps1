$root = Split-Path $PSScriptRoot -Parent
Start-Process powershell -ArgumentList '-NoExit','-Command',"Set-Location '$root\backend'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
Start-Process powershell -ArgumentList '-NoExit','-Command',"Set-Location '$root\frontend'; npm run dev"
