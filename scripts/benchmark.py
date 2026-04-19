"""
benchmark.py — Benchmark LLM inference speed on AMD GPU via llama.cpp Vulkan.

Reports prompt processing (pp) and token generation (tg) tokens/sec.
"""
import argparse
import sys
import time
from pathlib import Path


BENCH_PROMPT = (
    "Write a detailed explanation of how transformers work in machine learning, "
    "covering attention mechanisms, positional encoding, and the encoder-decoder architecture."
)
BENCH_TOKENS = 128


def parse_args():
    p = argparse.ArgumentParser(description="Benchmark llama.cpp on AMD GPU")
    p.add_argument("--model", default=None, help="Path to GGUF model (auto-detect if omitted)")
    p.add_argument("--gpu-layers", type=int, default=-1,
                   help="GPU layers to offload (-1 = all)")
    p.add_argument("--ctx", type=int, default=2048)
    p.add_argument("--runs", type=int, default=3, help="Number of benchmark runs")
    p.add_argument("--tokens", type=int, default=BENCH_TOKENS,
                   help="Tokens to generate per run")
    return p.parse_args()


def find_model_auto():
    models_dir = Path("models")
    if models_dir.exists():
        ggufs = sorted(models_dir.glob("*.gguf"))
        if ggufs:
            return str(ggufs[0])
    return None


def run_benchmark(llm, prompt, max_tokens, runs):
    results = []

    for i in range(runs):
        # Warm-up on first run
        if i == 0:
            print("  Warmup pass...")
            llm(prompt, max_tokens=16, echo=False)

        print(f"  Run {i + 1}/{runs}...")
        t0 = time.time()
        out = llm(prompt, max_tokens=max_tokens, echo=False, stream=False)
        elapsed = time.time() - t0

        usage = out.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", len(prompt.split()))
        completion_tokens = usage.get("completion_tokens", max_tokens)

        tg_tps = completion_tokens / elapsed if elapsed > 0 else 0
        results.append({
            "elapsed": elapsed,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "tg_tps": tg_tps,
        })
        print(f"    {completion_tokens} tokens in {elapsed:.2f}s = {tg_tps:.1f} t/s")

    return results


def main():
    args = parse_args()

    print("=== llama.cpp AMD Vulkan Benchmark ===\n")

    try:
        from llama_cpp import Llama
    except ImportError:
        print("ERROR: llama_cpp not installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    model_path = args.model or find_model_auto()
    if not model_path:
        print("ERROR: No model found in models/ directory.")
        print("  Run: python scripts\\download_model.py --model llama3.1-8b-q4")
        sys.exit(1)

    if not Path(model_path).exists():
        print(f"ERROR: Model not found: {model_path}")
        sys.exit(1)

    print(f"Model      : {Path(model_path).name}")
    print(f"GPU layers : {'all' if args.gpu_layers == -1 else args.gpu_layers}")
    print(f"Context    : {args.ctx}")
    print(f"Runs       : {args.runs}")
    print(f"Tokens/run : {args.tokens}")
    print()

    print("Loading model...")
    t_load = time.time()
    llm = Llama(
        model_path=model_path,
        n_gpu_layers=args.gpu_layers,
        n_ctx=args.ctx,
        verbose=False,
    )
    load_time = time.time() - t_load
    print(f"Load time  : {load_time:.2f}s\n")

    print("Running benchmark...")
    results = run_benchmark(llm, BENCH_PROMPT, args.tokens, args.runs)

    avg_tps = sum(r["tg_tps"] for r in results) / len(results)
    min_tps = min(r["tg_tps"] for r in results)
    max_tps = max(r["tg_tps"] for r in results)

    print(f"\n=== Results ===")
    print(f"Model      : {Path(model_path).name}")
    print(f"Load time  : {load_time:.2f}s")
    print(f"Avg t/s    : {avg_tps:.1f}")
    print(f"Min t/s    : {min_tps:.1f}")
    print(f"Max t/s    : {max_tps:.1f}")
    print(f"GPU layers : {'all' if args.gpu_layers == -1 else args.gpu_layers}")

    del llm


if __name__ == "__main__":
    main()
