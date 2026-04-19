@echo off
REM llm-amd-windows — Quick Start
REM AMD GPU local LLM inference via llama.cpp Vulkan

echo ============================================
echo  Local LLM — AMD GPU (llama.cpp + Vulkan)
echo ============================================
echo.

REM Activate venv if present
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check llama_cpp
python -c "import llama_cpp" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Installation failed.
        echo If the Vulkan wheel isn't available, build from source:
        echo   set CMAKE_ARGS=-DLLAMA_VULKAN=on
        echo   pip install llama-cpp-python --no-binary llama-cpp-python
        pause
        exit /b 1
    )
)

REM Verify GPU
echo.
echo Verifying GPU...
python scripts\verify_gpu.py

REM Check for a model
echo.
if not exist "models\*.gguf" (
    echo No model found. Downloading Llama 3.1 8B Q4...
    python scripts\download_model.py --model llama3.1-8b-q4
    if errorlevel 1 (
        echo Download failed. Please download a model manually.
        echo   python scripts\download_model.py --list
        pause
        exit /b 1
    )
)

REM Start chat
echo.
echo Starting chat...
python scripts\chat.py --gpu-layers -1 --ctx 4096

pause
