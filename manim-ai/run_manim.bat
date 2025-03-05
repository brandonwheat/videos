@echo off
REM Activate the virtual environment
call "%~dp0venv\Scripts\activate.bat"

REM Add MiKTeX bin directory to PATH
set PATH=%PATH%;C:\Users\Brandon\AppData\Local\Programs\MiKTeX\miktex\bin\x64

REM Run manim with the provided arguments
manim %*

REM Deactivate the virtual environment
call deactivate 