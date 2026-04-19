"""
download_model.py — Download GGUF models from HuggingFace for llama.cpp.

Usage:
    python scripts/download_model.py --model llama3.1-8b-q4
    python scripts/download_model.py --model mistral-7b-q4
    python scripts/download_model.py --list
    python scripts/download_model.py --url https://huggingface.co/bartowski/.../model.gguf
"""
import argparse
import os
import sys
import urllib.request
from pathlib import Path


PRESETS = {
    # Format: alias -> (repo_id, filename, size_hint)
    "llama3.1-8b-q4": (
        "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",
        "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
        "4.9GB",
    ),
    "llama3.1-8b-q5": (
        "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",
        "Meta-Llama-3.1-8B-Instruct-Q5_K_M.gguf",
        "5.7GB",
    ),
    "llama3.1-70b-q4": (
        "bartowski/Meta-Llama-3.1-70B-Instruct-GGUF",
        "Meta-Llama-3.1-70B-Instruct-Q4_K_M.gguf",
        "42GB",
    ),
    "mistral-7b-q4": (
        "bartowski/Mistral-7B-Instruct-v0.3-GGUF",
        "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
        "4.4GB",
    ),
    "phi3-mini-q4": (
        "bartowski/Phi-3.5-mini-instruct-GGUF",
        "Phi-3.5-mini-instruct-Q4_K_M.gguf",
        "2.2GB",
    ),
    "phi3-medium-q4": (
        "bartowski/Phi-3-medium-128k-instruct-GGUF",
        "Phi-3-medium-128k-instruct-Q4_K_M.gguf",
        "7.6GB",
    ),
    "qwen2.5-7b-q4": (
        "bartowski/Qwen2.5-7B-Instruct-GGUF",
        "Qwen2.5-7B-Instruct-Q4_K_M.gguf",
        "4.7GB",
    ),
    "qwen2.5-14b-q4": (
        "bartowski/Qwen2.5-14B-Instruct-GGUF",
        "Qwen2.5-14B-Instruct-Q4_K_M.gguf",
        "8.9GB",
    ),
    "gemma2-9b-q4": (
        "bartowski/gemma-2-9b-it-GGUF",
        "gemma-2-9b-it-Q4_K_M.gguf",
        "5.8GB",
    ),
    "deepseek-r1-7b-q4": (
        "bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF",
        "DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf",
        "4.7GB",
    ),
    "codestral-22b-q4": (
        "bartowski/Codestral-22B-v0.1-GGUF",
        "Codestral-22B-v0.1-Q4_K_M.gguf",
        "13GB",
    ),
}


def parse_args():
    p = argparse.ArgumentParser(description="Download GGUF models for llama.cpp")
    p.add_argument("--model", default=None, help="Preset name or HuggingFace repo/filename")
    p.add_argument("--url", default=None, help="Direct download URL for a .gguf file")
    p.add_argument("--output-dir", default="models", help="Download directory [default: models]")
    p.add_argument("--list", action="store_true", help="List all available presets")
    p.add_argument("--force", action="store_true", help="Re-download if file exists")
    return p.parse_args()


def show_presets():
    print("Available model presets:\n")
    print(f"  {'Alias':<25} {'Size':<8} {'Description'}")
    print(f"  {'-'*25} {'-'*8} {'-'*40}")
    for alias, (repo, filename, size) in sorted(PRESETS.items()):
        desc = filename.replace(".gguf", "").replace("-", " ")
        print(f"  {alias:<25} {size:<8} {desc}")
    print()
    print("Usage: python scripts/download_model.py --model <alias>")


def download_with_progress(url, dest_path):
    """Download a file with a simple progress indicator."""
    print(f"Downloading: {url}")
    print(f"Saving to  : {dest_path}")

    def reporthook(count, block_size, total_size):
        if total_size > 0:
            percent = min(int(count * block_size * 100 / total_size), 100)
            mb_done = count * block_size / 1024 / 1024
            mb_total = total_size / 1024 / 1024
            print(f"\r  {percent:3d}% — {mb_done:.0f}/{mb_total:.0f} MB", end="", flush=True)

    try:
        urllib.request.urlretrieve(url, dest_path, reporthook)
        print()  # newline after progress
        return True
    except Exception as e:
        print(f"\nERROR: Download failed: {e}")
        if Path(dest_path).exists():
            Path(dest_path).unlink()
        return False


def download_via_huggingface_hub(repo_id, filename, output_dir, force):
    """Download using huggingface_hub if available."""
    try:
        from huggingface_hub import hf_hub_download
        dest = Path(output_dir) / filename
        if dest.exists() and not force:
            print(f"Already exists: {dest}")
            print("  Use --force to re-download.")
            return True
        print(f"Downloading from HuggingFace Hub...")
        print(f"  Repo    : {repo_id}")
        print(f"  File    : {filename}")
        local = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=output_dir,
        )
        print(f"Saved to: {local}")
        return True
    except ImportError:
        # Fall back to direct URL
        return None


def main():
    args = parse_args()

    if args.list:
        show_presets()
        return

    if not args.model and not args.url:
        print("ERROR: Specify --model or --url. Use --list to see presets.")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Direct URL download
    if args.url:
        filename = args.url.split("/")[-1].split("?")[0]
        dest = output_dir / filename
        if dest.exists() and not args.force:
            print(f"Already exists: {dest} (use --force to re-download)")
            return
        ok = download_with_progress(args.url, str(dest))
        if ok:
            print(f"\nModel saved: {dest}")
            print(f"Run: python scripts\\chat.py --model {dest}")
        sys.exit(0 if ok else 1)

    # Preset
    if args.model not in PRESETS:
        print(f"ERROR: Unknown preset '{args.model}'. Use --list to see available models.")
        sys.exit(1)

    repo_id, filename, size = PRESETS[args.model]
    dest = output_dir / filename

    if dest.exists() and not args.force:
        print(f"Already downloaded: {dest}")
        print(f"Run: python scripts\\chat.py --model {dest}")
        return

    print(f"Model  : {args.model}")
    print(f"Size   : ~{size}")
    print()

    # Try huggingface_hub first
    result = download_via_huggingface_hub(repo_id, filename, str(output_dir), args.force)
    if result is None:
        # Fall back to direct URL
        url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
        ok = download_with_progress(url, str(dest))
        if not ok:
            sys.exit(1)
    elif not result:
        sys.exit(1)

    print(f"\nDownload complete: {dest}")
    print(f"\nTo start chatting:")
    print(f"  python scripts\\chat.py --model {dest}")


if __name__ == "__main__":
    main()
