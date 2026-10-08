@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Copiloto Inteligente de Viagem
py -3.12 copiloto.py
pause
