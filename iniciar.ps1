# Check & Activar Entorno Virtual
Write-Host "🌱 Iniciando Historias que Inspiran® en Entorno Local..." -ForegroundColor Green

$venvPath = ".\apps\api\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
} else {
    Write-Host "❌ No se encontró el entorno virtual en $venvPath" -ForegroundColor Red
    exit
}

# Iniciar Backend (FastAPI) en segundo plano
Write-Host "⚙️ Arrancando Backend API (Port 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$venvPath'; uvicorn main:app --app-dir apps/api --reload --port 8000"

# Iniciar Frontend (Streamlit)
Write-Host "🎨 Arrancando Frontend Web (Port 8501)..." -ForegroundColor Magenta
streamlit run apps/web/app.py
