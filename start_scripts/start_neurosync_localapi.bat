@echo off
TITLE "Neurosync Local API"
cd /d "%~dp0..\Neurosync\NeuroSync_Local_API"
:: Edit this line to match your installation path for Anaconda
call %USERPROFILE%\miniconda30\Scripts\activate.bat
::
call conda activate mcp_env_1
echo Starting Neurosync API from: %cd%
python neurosync_local_api.py
cmd /k