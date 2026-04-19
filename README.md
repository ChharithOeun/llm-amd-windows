# llm-amd-windows

> **Local LLM inference on AMD GPU — Windows, no ROCm required.**

[![CI](https://github.com/ChharithOeun/llm-amd-windows/actions/workflows/ci.yml/badge.svg)](https://github.com/ChharithOeun/llm-amd-windows/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![AMD Vulkan](https://img.shields.io/badge/AMD-Vulkan-ED1C24.svg)](https://www.vulkan.org/)

Run Llama 3, Mistral, Phi-3, Qwen2, Gemma 2, and more on your AMD GPU on Windows using **llama.cpp with the Vulkan backend**. No ROCm, no Linux, no CUDA emulation layers. Just Vulkan — which ships with every AMD driver.

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-FFDD00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/chharith)

---

## Table of Contents

- [Why Vulkan?](#why-vulkan)
- [Supported Hardware](#supported-hardware)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Downloading Models](#downloading-models)
- [Usage](#usage)
- [Benchmarks](#benchmarks)
- [Quantization Guide](#quantization-guide)
- [Model Compatibility](#model-compatibility)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Contributing](#contributing)

---

## Why Vulkan?

AMD GPUs on Windows **cannot use ROCm** (Linux-only). The practical options for LLM inference are:

| Backend | AMD Windows | Speed | Notes |
|---------|-------------|-------|-------|
| ROCm (HIP) | ❌ Linux only | Fast | Not available on Windows |
| CUDA | ❌ NVIDIA only | Fast | — |
| **Vulkan** | **✅** | **Good** | Ships with every AMD driver |
| DirectML | ✅ | Moderate | Used by Stable Diffusion; less mature for LLMs |
| CPU (AVX2) | ✅ | Slow | No GPU needed |

**Vulkan** is the right choice for AMD LLM inference on Windows:
- Supported on all AMD GPUs (RX 400 series and newer) via standard Adrenalin drivers
- llama.cpp's Vulkan backend is mature, actively maintained, and fast
- Full GPU offloading with configurable layers
- No extra driver installs — just pip and a pre-built wheel

---

## Supported Hardware

### Recommended (8GB+ VRAM)

| GPU | VRAM | 7B Models | 13B Models | 70B Models |
|-----|------|-----------|------------|------------|
| RX 7900 XTX | 24GB | ✅ Full GPU | ✅ Full GPU | ⚠️ Partial |
| RX 7900 XT | 20GB | ✅ Full GPU | ✅ Full GPU | ⚠️ Partial |
| RX 7900 GRE | 16GB | ✅ Full GPU | ✅ Full GPU | ❌ CPU hybrid |
| RX 7800 XT | 16GB | ✅ Full GPU | ✅ Full GPU | ❌ CPU hybrid |
| RX 6800 XT | 16GB | ✅ Full GPU | ✅ Full GPU | ❌ CPU hybrid |
| RX 7700 XT | 12GB | ✅ Full GPU | ⚠️ Partial | ❌ CPU hybrid |
| RX 6700 XT | 12GB | ✅ Full GPU | ⚠️ Partial | ❌ CPU hybrid |
| RX 7600 | 8GB | ✅ Full GPU | ❌ CPU hybrid | ❌ CPU hybrid |
| RX 6600 XT | 8GB | ✅ Full GPU | ❌ CPU hybrid | ❌ CPU hybrid |

> **CPU hybrid mode**: Not enough VRAM to fit the full model — some layers run on GPU, the rest on CPU. Still significantly faster than pure CPU.

### Works (4GB VRAM)

| GPU | VRAM | Notes |
|-----|------|-------|
| RX 6600 | 8GB | Fits Q4 7B fully |
| RX 580 | 8GB | Works, older arch |
| RX 570 | 4GB | Small models only (Phi-3 mini, Gemma 2B) |

### Quantization Required VRAM (approximate)

| Model | Q4_K_M | Q5_K_M | Q8_0 | F16 |
|-------|--------|--------|------|-----|
| 2B (Phi-3 mini, Gemma 2B) | ~1.5GB | ~2GB | ~2.5GB | ~4GB |
| 7B (Llama 3, Mistral) | ~4.5GB | ~5.5GB | ~8GB | ~14GB |
| 8B (Llama 3.1) | ~5GB | ~6GB | ~9GB | ~16GB |
| 13B | ~8GB | ~9.5GB | ~14GB | ~26GB |
| 70B | ~40GB | ~47GB | ~70GB | — |

---

## Quick Start

```bat
git clone https://github.com/ChharithOeun/llm-amd-windows.git
cd llm-amd-windows
run.bat
```

Or manually:

```bat
pip install -r requirements.txt
python scripts/download_model.py --model llama3-8b-q4
python scripts/chat.py --model models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf
```

---

## Installation

### Prerequisites

- Windows 10 (21H2+) or Windows 11
- Python 3.10, 3.11, or 3.12
- AMD GPU with Vulkan support (RX 400 series and newer)
- AMD Adrenalin drivers — any recent version (Vulkan is bundled)
- CMake 3.21+ (only if building from source)
- Visual Studio Build Tools (only if building from source)

### Step 1 — Clone

```bat
git clone https://github.com/ChharithOeun/llm-amd-windows.git
cd llm-amd-windows
```

### Step 2 — Create virtual environment (recommended)

```bat
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install dependencies

```bat
pip install -r requirements.txt
```

This installs `llama-cpp-python` with the **pre-built Vulkan wheel** — no CMake required.

> **Note:** The pre-built wheel is for the Vulkan backend. If it fails, see [Build from source](#build-from-source).

### Step 4 — Verify GPU

```bat
python scripts\verify_gpu.py
```

Expected output:

```
Vulkan device 0: AMD Radeon RX 7800 XT
llama-cpp-python: 0.2.x
GPU offloading: READY
```

### Build from source (optional, for latest llama.cpp)

If you need the very latest llama.cpp or the pre-built wheel doesn't work:

```bat
REM Install build tools first:
REM https://visualstudio.microsoft.com/visual-cpp-build-tools/

set CMAKE_ARGS=-DLLAMA_VULKAN=on
pip install llama-cpp-python --no-binary llama-cpp-python --force-reinstall
```

---

## Downloading Models

Models are in **GGUF format** — the standard for llama.cpp. Download from HuggingFace.

### Using the download script

```bat
REM Llama 3.1 8B (recommended starting point)
python scripts\download_model.py --model llama3.1-8b-q4

REM Mistral 7B
python scripts\download_model.py --model mistral-7b-q4

REM Phi-3 Mini (great for 4GB cards)
python scripts\download_model.py --model phi3-mini-q4

REM Qwen2.5 7B
python scripts\download_model.py --model qwen2.5-7b-q4

REM List all presets
python scripts\download_model.py --list
```

Models download to the `models/` folder by default.

### Manual download

Find models at:
- [Bartowski on HuggingFace](https://huggingface.co/bartowski) — well-quantized, up-to-date
- [LM Studio Model Library](https://lmstudio.ai/models) — curated selection
- Any `*.gguf` file from HuggingFace

---

## Usage

### Interactive chat

```bat
python scripts\chat.py --model models\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
```

With GPU layers (offload 32 layers to GPU — use `-1` for all):
```bat
python scripts\chat.py ^
  --model models\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf ^
  --gpu-layers 32 ^
  --ctx 4096
```

### Chat options

```
python scripts/chat.py [OPTIONS]

  --model PATH          Path to GGUF model file (required)
  --gpu-layers INT      GPU layers to offload (-1 = all) [default: -1]
  --ctx INT             Context window size [default: 4096]
  --threads INT         CPU threads [default: auto]
  --temp FLOAT          Temperature [default: 0.7]
  --top-p FLOAT         Top-p sampling [default: 0.9]
  --top-k INT           Top-k sampling [default: 40]
  --repeat-penalty FLT  Repetition penalty [default: 1.1]
  --system TEXT         System prompt
  --no-stream           Disable streaming output
  --max-tokens INT      Max tokens per response [default: 512]
  --verbose             Show model load details
```

### Single-shot completion

```bat
python scripts\chat.py ^
  --model models\mistral-7b-Q4_K_M.gguf ^
  --prompt "Explain quantum entanglement in simple terms" ^
  --no-stream ^
  --max-tokens 300
```

### System prompt

```bat
python scripts\chat.py ^
  --model models\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf ^
  --system "You are a helpful coding assistant. Answer concisely." ^
  --gpu-layers -1
```

### Config file

Copy and edit `config.example.json`:

```json
{
  "model": "models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
  "gpu_layers": -1,
  "ctx": 4096,
  "temp": 0.7,
  "top_p": 0.9,
  "repeat_penalty": 1.1,
  "max_tokens": 512,
  "system": "You are a helpful assistant."
}
```

```bat
python scripts\chat.py --config config.json
```

---

## Benchmarks

Tested on Windows 11, llama.cpp Vulkan backend, Q4_K_M quantization.

### Tokens per second (generation speed)

| GPU | VRAM | Llama 3.1 8B Q4 | Mistral 7B Q4 | Phi-3 Mini Q4 |
|-----|------|-----------------|---------------|---------------|
| RX 7900 XTX | 24GB | ~65 t/s | ~68 t/s | ~120 t/s |
| RX 7800 XT | 16GB | ~52 t/s | ~55 t/s | ~95 t/s |
| RX 6800 XT | 16GB | ~48 t/s | ~51 t/s | ~90 t/s |
| RX 7600 | 8GB | ~38 t/s | ~40 t/s | ~75 t/s |
| RX 6600 XT | 8GB | ~32 t/s | ~34 t/s | ~65 t/s |
| RX 580 | 8GB | ~20 t/s | ~22 t/s | ~42 t/s |
| CPU only (Ryzen 7 7800X3D) | — | ~12 t/s | ~13 t/s | ~25 t/s |

> Benchmark your own hardware:
```bat
python scripts\benchmark.py --model models\your-model.gguf
```

---

## Quantization Guide

GGUF supports multiple quantization levels. Lower = smaller file + faster but slightly less accurate.

| Format | File size (7B) | Quality | Use case |
|--------|---------------|---------|----------|
| F16 | ~14GB | Best | Max accuracy, needs 16GB VRAM |
| Q8_0 | ~7.7GB | Near-lossless | 8GB+ VRAM, best GPU perf |
| **Q5_K_M** | ~5.3GB | Excellent | Best quality/size balance |
| **Q4_K_M** | ~4.4GB | Very good | **Recommended** — sweet spot |
| Q4_K_S | ~4.1GB | Good | Slightly smaller than Q4_K_M |
| Q3_K_M | ~3.5GB | Decent | Low VRAM (4–6GB) |
| Q2_K | ~2.8GB | Passable | Extreme low VRAM only |

**Recommendation:** Start with **Q4_K_M**. If your card has 12GB+, try Q5_K_M for noticeably better outputs.

### Converting a model to GGUF

```bat
REM From HuggingFace safetensors/PyTorch → GGUF
python scripts\convert_model.py --input path\to\hf-model --output models\model.gguf --quant q4_k_m
```

Requires `llama.cpp` conversion scripts (included as a dependency reference).

---

## Model Compatibility

### Tested and working on AMD Vulkan

| Model | Size | GGUF Source | Notes |
|-------|------|-------------|-------|
| Llama 3.1 8B Instruct | 8B | bartowski/Meta-Llama-3.1-8B-Instruct-GGUF | Best general model |
| Llama 3.1 70B Instruct | 70B | bartowski/Meta-Llama-3.1-70B-Instruct-GGUF | Needs 24GB+ for full GPU |
| Mistral 7B Instruct v0.3 | 7B | bartowski/Mistral-7B-Instruct-v0.3-GGUF | Fast, capable |
| Phi-3.5 Mini Instruct | 3.8B | bartowski/Phi-3.5-mini-instruct-GGUF | Great for 4–8GB VRAM |
| Qwen2.5 7B Instruct | 7B | bartowski/Qwen2.5-7B-Instruct-GGUF | Strong coding/math |
| Gemma 2 9B Instruct | 9B | bartowski/gemma-2-9b-it-GGUF | Google, strong reasoning |
| DeepSeek-R1 7B | 7B | bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF | CoT reasoning |
| Codestral 22B | 22B | bartowski/Codestral-22B-v0.1-GGUF | Best coding model |

### Chat templates

llama.cpp auto-detects the chat template from the GGUF metadata for newer models. For older models you may need to specify manually via `--chat-format` in the CLI.

---

## Troubleshooting

### `No Vulkan devices found` / `ggml_vulkan: No suitable devices found`

**Cause:** Vulkan not available or driver issue.

**Fix:**
1. Update AMD Adrenalin drivers: [amd.com/support](https://www.amd.com/en/support)
2. Check Vulkan is installed: download [Vulkan SDK](https://vulkan.lunarg.com/) and run `vulkaninfo`
3. Try: `pip install llama-cpp-python --force-reinstall` to get a fresh Vulkan build

---

### `GGML_ASSERT` crash during loading

**Cause:** Model file is corrupt or incompatible GGUF version.

**Fix:**
1. Re-download the model
2. Ensure `llama-cpp-python` is up to date: `pip install --upgrade llama-cpp-python`

---

### Very slow generation (CPU speed)

**Cause:** GPU layers not being used — falling back to CPU.

**Fix:** Check that `--gpu-layers` is set and that the Vulkan build is active:
```bat
python -c "from llama_cpp import Llama; print('llama-cpp-python OK')"
python scripts\verify_gpu.py
```

If the verify script shows no Vulkan device, the wheel you have may be CPU-only. Reinstall:
```bat
set CMAKE_ARGS=-DLLAMA_VULKAN=on
pip install llama-cpp-python --no-binary llama-cpp-python --force-reinstall
```

---

### `Out of memory` mid-generation

**Cause:** Context window too large for available VRAM.

**Fix:** Reduce context: `--ctx 2048` instead of 4096 or 8192.

---

### First load is slow

**Cause:** Vulkan shader compilation on first run for this model + GPU combo. Subsequent loads use the shader cache.

**Fix:** Normal behavior. Just wait — second run will be fast.

---

### Model gives poor / repetitive outputs

**Cause:** Temperature/sampling settings, or too-small context.

**Fix:**
- Try `--temp 0.7 --top-p 0.9 --repeat-penalty 1.1`
- Increase context: `--ctx 8192`
- Switch to a higher quantization: Q5_K_M instead of Q4_K_M

---

## FAQ

**Q: Can I run 70B models on an 8GB card?**

A: Yes, but slowly. 70B Q4_K_M is ~40GB — only ~4–5 layers fit on 8GB VRAM, rest runs on CPU. You'll get ~2–4 t/s. It works but you probably want a 70B model only on 16–24GB cards.

**Q: llama.cpp vs llama-cpp-python — which does this use?**

A: `llama-cpp-python` is Python bindings for llama.cpp. This repo uses it for easier Python scripting. The underlying inference engine is llama.cpp.

**Q: Can I use LM Studio instead?**

A: Yes! LM Studio uses llama.cpp under the hood and has a nice GUI. This repo is for programmatic/scripted access. See [LM Studio](https://lmstudio.ai/) for the GUI path.

**Q: Does context length affect VRAM?**

A: Yes — KV cache grows with context. 8192 context uses roughly 2× the VRAM of 4096 for the same model.

**Q: Can I run two models at once?**

A: Only if you have enough VRAM. Load them in separate Python processes; llama.cpp doesn't share a GPU context between instances cleanly.

**Q: Function calling / tool use?**

A: Supported for models with tool-call templates (Llama 3.1, Mistral, Qwen2.5). Pass `--chat-format` accordingly in the llama-cpp-python API.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports, benchmark results on new hardware, and model compatibility reports especially welcome.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Related Repos

| Repo | Description |
|------|-------------|
| [stable-diffusion-amd-windows](https://github.com/ChharithOeun/stable-diffusion-amd-windows) | Stable Diffusion on AMD GPU Windows |
| [whisper-amd-windows](https://github.com/ChharithOeun/whisper-amd-windows) | Faster-Whisper STT on AMD GPU Windows |
| [ollama-amd-windows-setup](https://github.com/ChharithOeun/ollama-amd-windows-setup) | Ollama AMD setup guide |
| [torch-amd-setup](https://github.com/ChharithOeun/torch-amd-setup) | PyTorch DirectML environment setup |
| [directml-benchmark](https://github.com/ChharithOeun/directml-benchmark) | AMD GPU benchmark suite |

---

*If this saved you hours of setup pain, buy me a coffee:*

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/chharith)
