@echo off
TITLE ControlPanel
cd /d "%~dp0.."
:: Edit this line to match your installation path for Anaconda
call %USERPROFILE%\miniconda30\Scripts\activate.bat
::
call conda activate mcp_env_1
python control_panel.py
cmd /k