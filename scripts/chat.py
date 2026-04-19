"""
chat.py — Interactive chat with local LLMs via llama-cpp-python (Vulkan backend).

Usage:
    python scripts/chat.py --model models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
    python scripts/chat.py --model models/mistral-7b-Q4_K_M.gguf --gpu-layers 32 --ctx 8192
    python scripts/chat.py --help
"""
import argparse
import json
import sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(
        description="Chat with local LLMs on AMD GPU via llama.cpp Vulkan",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--model", default=None, help="Path to GGUF model file")
    p.add_argument("--gpu-layers", type=int, default=-1,
                   help="Layers to offload to GPU (-1 = all) [default: -1]")
    p.add_argument("--ctx", type=int, default=4096, help="Context window size [default: 4096]")
    p.add_argument("--threads", type=int, default=None,
                   help="CPU threads for non-GPU layers [default: auto]")
    p.add_argument("--temp", type=float, default=0.7, help="Temperature [default: 0.7]")
    p.add_argument("--top-p", type=float, default=0.9, help="Top-p [default: 0.9]")
    p.add_argument("--top-k", type=int, default=40, help="Top-k [default: 40]")
    p.add_argument("--repeat-penalty", type=float, default=1.1,
                   help="Repetition penalty [default: 1.1]")
    p.add_argument("--max-tokens", type=int, default=512,
                   help="Max tokens per response [default: 512]")
    p.add_argument("--system", default="You are a helpful, concise assistant.",
                   help="System prompt")
    p.add_argument("--prompt", default=None,
                   help="Single prompt (non-interactive mode)")
    p.add_argument("--no-stream", action="store_true", help="Disable streaming output")
    p.add_argument("--verbose", action="store_true", help="Show model load details")
    p.add_argument("--config", default=None, help="Load settings from JSON config file")
    p.add_argument("--chat-format", default=None,
                   help="Chat format override (e.g. llama-3, chatml, mistral-instruct)")
    return p


def load_config(args, config_path):
    with open(config_path) as f:
        cfg = json.load(f)
    for key, val in cfg.items():
        attr = key.replace("-", "_")
        if hasattr(args, attr):
            current = getattr(args, attr)
            # Only override if the arg is at its default (None or not explicitly set)
            if current is None:
                setattr(args, attr, val)
    return args


def find_model_auto():
    """Auto-detect a model in models/ directory."""
    models_dir = Path("models")
    if models_dir.exists():
        ggufs = sorted(models_dir.glob("*.gguf"))
        if ggufs:
            return str(ggufs[0])
    return None


def load_llm(args):
    """Load llama.cpp model with Vulkan backend."""
    from llama_cpp import Llama

    model_path = args.model or find_model_auto()
    if not model_path:
        print("ERROR: No model specified and none found in models/ directory.")
        print("  Download one: python scripts\\download_model.py --model llama3.1-8b-q4")
        sys.exit(1)

    if not Path(model_path).exists():
        print(f"ERROR: Model not found: {model_path}")
        sys.exit(1)

    print(f"Loading: {Path(model_path).name}")
    print(f"GPU layers: {'all' if args.gpu_layers == -1 else args.gpu_layers}")
    print(f"Context: {args.ctx} tokens")

    kwargs = dict(
        model_path=model_path,
        n_gpu_layers=args.gpu_layers,
        n_ctx=args.ctx,
        verbose=args.verbose,
    )
    if args.threads:
        kwargs["n_threads"] = args.threads
    if args.chat_format:
        kwargs["chat_format"] = args.chat_format

    llm = Llama(**kwargs)
    print("Model loaded.\n")
    return llm


def stream_response(llm, messages, args):
    """Stream a response from the model."""
    tokens = 0
    text = ""
    for chunk in llm.create_chat_completion(
        messages=messages,
        max_tokens=args.max_tokens,
        temperature=args.temp,
        top_p=args.top_p,
        top_k=args.top_k,
        repeat_penalty=args.repeat_penalty,
        stream=True,
    ):
        delta = chunk["choices"][0]["delta"].get("content", "")
        if delta:
            print(delta, end="", flush=True)
            text += delta
            tokens += 1
    print()
    return text, tokens


def full_response(llm, messages, args):
    """Get a full (non-streamed) response."""
    result = llm.create_chat_completion(
        messages=messages,
        max_tokens=args.max_tokens,
        temperature=args.temp,
        top_p=args.top_p,
        top_k=args.top_k,
        repeat_penalty=args.repeat_penalty,
        stream=False,
    )
    text = result["choices"][0]["message"]["content"]
    tokens = result["usage"]["completion_tokens"]
    return text, tokens


def interactive_loop(llm, args):
    """Run interactive chat session."""
    messages = [{"role": "system", "content": args.system}]

    print("=" * 60)
    print("AMD LLM Chat  |  type 'quit' or Ctrl+C to exit")
    print("              |  type 'clear' to reset conversation")
    print("              |  type 'save' to save conversation log")
    print("=" * 60)
    print(f"System: {args.system[:80]}")
    print()

    import time

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if user_input.lower() == "clear":
            messages = [{"role": "system", "content": args.system}]
            print("Conversation cleared.\n")
            continue
        if user_input.lower() == "save":
            log_path = "chat_log.json"
            with open(log_path, "w") as f:
                json.dump(messages, f, indent=2)
            print(f"Saved to {log_path}\n")
            continue

        messages.append({"role": "user", "content": user_input})
        print("\nAssistant: ", end="", flush=True)

        t0 = time.time()
        if args.no_stream:
            text, tok = full_response(llm, messages, args)
            print(text)
        else:
            text, tok = stream_response(llm, messages, args)

        elapsed = time.time() - t0
        tps = tok / elapsed if elapsed > 0 else 0
        print(f"\n[{tok} tokens | {tps:.1f} t/s | {elapsed:.1f}s]\n")

        messages.append({"role": "assistant", "content": text})


def single_shot(llm, args):
    """Run single prompt and exit."""
    import time

    messages = [
        {"role": "system", "content": args.system},
        {"role": "user", "content": args.prompt},
    ]

    print(f"Prompt: {args.prompt}\n")
    print("Response:")

    t0 = time.time()
    if args.no_stream:
        text, tok = full_response(llm, messages, args)
        print(text)
    else:
        text, tok = stream_response(llm, messages, args)

    elapsed = time.time() - t0
    tps = tok / elapsed if elapsed > 0 else 0
    print(f"\n[{tok} tokens | {tps:.1f} t/s | {elapsed:.1f}s]")


def main():
    parser = parse_args()
    args = parser.parse_args()

    if args.config:
        args = load_config(args, args.config)

    try:
        from llama_cpp import Llama  # noqa: F401
    except ImportError:
        print("ERROR: llama_cpp not installed.")
        print("  Run: pip install -r requirements.txt")
        sys.exit(1)

    llm = load_llm(args)

    if args.prompt:
        single_shot(llm, args)
    else:
        interactive_loop(llm, args)


if __name__ == "__main__":
    main()
