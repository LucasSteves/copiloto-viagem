@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Copiloto Inteligente de Viagem
echo ============================================================
echo   COPILOTO INTELIGENTE DE VIAGEM
echo   Instalacao automatica + execucao
echo ============================================================
echo.

REM 1) Confirma que o Python 3.12 esta instalado
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python 3.12 nao encontrado.
    echo.
    echo Instale o Python 3.12 em: https://www.python.org/downloads/
    echo Marque a caixa "Add python.exe to PATH" durante a instalacao.
    echo Depois rode este arquivo novamente.
    echo.
    pause
    exit /b 1
)

echo Python encontrado:
py -3.12 --version
echo.
echo Instalando as bibliotecas (na primeira vez demora alguns minutos)...
echo ------------------------------------------------------------
py -3.12 -m pip install --upgrade pip
py -3.12 -m pip install -r requirements.txt
py -3.12 -m pip install -r requirements-emocao.txt
py -3.12 -m pip install -r requirements-imagem.txt
echo ------------------------------------------------------------
echo.

if errorlevel 1 (
    echo [AVISO] Algo pode ter falhado na instalacao. Veja as mensagens acima.
    echo Se aparecer erro de "caminho longo", ligue o suporte a caminho longo do Windows.
    echo.
    pause
)

echo Iniciando o sistema...
echo (Na PRIMEIRA execucao ele baixa o modelo de voz ~360 MB - aguarde.)
echo.
py -3.12 copiloto.py
echo.
echo ============================================================
echo   Programa encerrado.
echo ============================================================
pause
