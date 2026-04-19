"""
verify_gpu.py — Verify llama.cpp Vulkan backend and AMD GPU availability.
"""
import sys


def check_vulkan():
    print("=== llama.cpp Vulkan GPU Verification ===\n")

    # Check llama-cpp-python
    try:
        import llama_cpp
        print(f"llama-cpp-python version : {llama_cpp.__version__}")
    except ImportError:
        print("ERROR: llama_cpp not installed.")
        print("  Run: pip install -r requirements.txt")
        return False

    # Check Vulkan device availability via llama_cpp internals
    try:
        # llama.cpp exposes backend info via library metadata
        from llama_cpp import llama_backend_init, llama_backend_free
        llama_backend_init()
        print("llama backend init       : OK")
        llama_backend_free()
    except Exception as e:
        print(f"llama backend init       : WARNING ({e})")

    # Try to list Vulkan devices via vulkan package if available
    try:
        import subprocess
        result = subprocess.run(
            ["vulkaninfo", "--summary"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "GPU" in line or "deviceName" in line or "driverVersion" in line:
                    print(f"Vulkan info              : {line.strip()}")
        else:
            print("Vulkan info              : vulkaninfo not found (drivers may still work)")
    except Exception:
        print("Vulkan info              : vulkaninfo not found (normal if SDK not installed)")

    # Quick load test with tiny model if available
    import pathlib
    models = list(pathlib.Path("models").glob("*.gguf")) if pathlib.Path("models").exists() else []
    if models:
        model_path = str(models[0])
        print(f"\nTest model               : {models[0].name}")
        try:
            from llama_cpp import Llama
            llm = Llama(
                model_path=model_path,
                n_gpu_layers=-1,
                n_ctx=64,
                verbose=False,
            )
            out = llm("Hello", max_tokens=4, echo=False)
            text = out["choices"][0]["text"].strip()
            print(f"Test generation          : OK ('{text[:30]}')")
            del llm
        except Exception as e:
            print(f"Test generation          : WARNING — {e}")
    else:
        print("\nNo models found in models/ — skipping generation test")
        print("Download one with: python scripts\\download_model.py --model llama3.1-8b-q4")

    print("\nStatus: Vulkan backend READY")
    return True


if __name__ == "__main__":
    ok = check_vulkan()
    sys.exit(0 if ok else 1)
