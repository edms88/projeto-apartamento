@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Instale Python 3.11 ou superior com o launcher py e tente novamente.
  pause
  exit /b 1
)
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
if not exist .venv\Scripts\python.exe goto erro
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto erro
.venv\Scripts\python.exe -m streamlit run app.py --server.address localhost
if errorlevel 1 goto erro
exit /b 0
:erro
 echo Nao foi possivel iniciar. Confira Python e a conexao com a internet.
 pause
 exit /b 1
