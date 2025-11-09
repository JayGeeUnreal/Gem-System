@echo off
TITLE "Neurosync Watcher To Face"
cd /d "%~dp0..\Neurosync\NeuroSync_Local_API"
:: Edit this line to match your installation path for Anaconda
call %USERPROFILE%\miniconda30\Scripts\activate.bat
::
call conda activate mcp_env_1
python watcher_to_face.py
cmd /k