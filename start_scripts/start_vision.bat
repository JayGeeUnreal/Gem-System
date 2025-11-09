@echo off
TITLE Vision
cd /d "%~dp0.."
:: Edit this line to match your installation path for Anaconda
call %USERPROFILE%\miniconda30\Scripts\activate.bat
::
call conda activate mcp_env_1
call Python vision.py
cmd /k