@echo off
echo ========================================
echo    EOS Report App - Avvio in corso...
echo ========================================
echo.

cd /d "%~dp0"

:: Controlla se streamlit è installato
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Installazione dipendenze...
    pip install -r requirements.txt
)

:: Controlla deep-translator
pip show deep-translator >nul 2>&1
if errorlevel 1 (
    echo Installazione deep-translator...
    pip install deep-translator
)

echo.
echo Avvio app su http://localhost:8503
echo.
streamlit run app.py --server.port 8503

pause
