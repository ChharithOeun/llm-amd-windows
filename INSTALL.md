# Installation Guide

## Requirements

- Windows 10 (21H2+) or Windows 11
- Python 3.10, 3.11, or 3.12
- AMD GPU with Vulkan support (RX 400 series and newer)
- AMD Adrenalin drivers — any version from the last 2 years works
- ~5GB disk space for a 7B Q4 model

## Quick Install

```bat
git clone https://github.com/ChharithOeun/llm-amd-windows.git
cd llm-amd-windows
pip install -r requirements.txt
python scripts\download_model.py --model llama3.1-8b-q4
python scripts\chat.py
```

## Detailed Steps

### 1. Python

Download from [python.org](https://www.python.org/downloads/). Check **"Add to PATH"** during install.

### 2. Virtual environment (recommended)

```bat
python -m venv venv
venv\Scripts\activate
```

### 3. Install llama-cpp-python

```bat
pip install -r requirements.txt
```

The `llama-cpp-python` package comes as a **pre-built Vulkan wheel** — no CMake needed.

If the pre-built wheel fails, build from source (requires [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)):

```bat
set CMAKE_ARGS=-DLLAMA_VULKAN=on
pip install llama-cpp-python --no-binary llama-cpp-python --force-reinstall
```

### 4. Verify

```bat
python scripts\verify_gpu.py
```

### 5. Download a model

```bat
python scripts\download_model.py --model llama3.1-8b-q4
```

### 6. Chat

```bat
python scripts\chat.py
```

## Updating

```bat
git pull
pip install -r requirements.txt --upgrade
```
