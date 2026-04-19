# Changelog

All notable changes will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Features

- Initial release: llama.cpp Vulkan backend for AMD GPUs on Windows
- `chat.py` — interactive chat with streaming output, conversation history, save/clear commands
- `benchmark.py` — tokens/sec benchmark with warmup and multi-run averaging
- `download_model.py` — 11 preset GGUF models with HuggingFace Hub integration
- `verify_gpu.py` — Vulkan device and llama-cpp-python verification
- GPU layer offloading with configurable `--gpu-layers` flag
- Context size control, temperature/top-p/top-k sampling params
- JSON config file support
- Single-shot and interactive modes
- System prompt support
- Chat format detection for Llama 3, Mistral, Phi-3, Qwen2.5, Gemma 2
