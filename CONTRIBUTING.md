# Contributing

Contributions welcome — hardware benchmarks, model compatibility reports, and bug fixes especially.

## Most wanted

- **Benchmark results** on GPUs not yet in the table (submit via issue or PR)
- **Model compatibility** notes — which GGUF models work well on AMD Vulkan
- **Bug fixes** for edge cases (unusual GPU models, older drivers)
- **Windows 10 compatibility** testing

## How to contribute

1. Fork the repo
2. Create a branch: `git checkout -b fix/your-fix`
3. Make your changes
4. Test on AMD hardware if possible
5. Submit a pull request

## Reporting bugs

Use the [Bug Report](https://github.com/ChharithOeun/llm-amd-windows/issues/new?template=bug_report.md) template. Always include:

- GPU model and VRAM
- AMD driver version
- Python version
- `llama-cpp-python` version (`pip show llama-cpp-python`)
- Full error traceback
- Exact command that failed
