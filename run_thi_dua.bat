@echo off
cd /d "%~dp0"
title TRO LY XET THI DUA
echo ==========================================
echo      DANG KHOI DONG TRO LY XET THI DUA
echo ==========================================
echo.
python -m streamlit run app.py
pause