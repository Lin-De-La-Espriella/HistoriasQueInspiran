@echo off
title Historias que Inspiran® - Despliegue Automatico
color 0A

echo ========================================================
echo   HISTORIAS QUE INSPIRAN (R) - DESPLIEGUE EN LA NUBE
echo ========================================================
echo.

:: 1. Ir a la carpeta del proyecto
cd /d "%~dp0"

:: 2. Preguntar el mensaje del commit (Opcional)
set /p commit_msg="Introduce la descripcion del cambio (presiona ENTER para usar la por defecto): "

if "%commit_msg%"=="" (
    set commit_msg="update: actualizacion automatica de la plataforma"
)

echo.
echo [1/3] Guardando cambios en Git...
git add .

echo [2/3] Creando punto de restauracion (Commit)...
git commit -m "%commit_msg%"

echo [3/3] Subiendo cambios a la nube (GitHub / Streamlit Cloud / Render)...
git push origin master

echo.
echo ========================================================
echo   ¡DESPLIEGUE EXITOSO! LA WEB SE ACTUALIZARA EN SEGUNDOS.
echo ========================================================
echo.
pause