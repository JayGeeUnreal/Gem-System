@echo off
TITLE StyleTTS2
cd /d "%~dp0.."
:: Edit this line to match your installation path for Anaconda
call %USERPROFILE%\miniconda30\Scripts\activate.bat
::
call conda activate styletts2
call python watcher.py
cmd /k