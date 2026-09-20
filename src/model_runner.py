import argparse
import time

import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

from prompt_builder import build_prompt
from utils import load_config


def load_model(model_id: str):
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto",
    )
    return model, tokenizer


def generate(
    model,
    tokenizer,
    prompt: str,
    do_sample: bool = False,
    temperature: float = 0.0,
    max_new_tokens: int = 150,
) -> tuple[str, float]:
    """Runs one generation call. Returns (response_text, seconds_taken)."""
    messages = [{"role": "user", "content": prompt}]
    chat_input = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(chat_input, return_tensors="pt").to(model.device)

    gen_kwargs = dict(max_new_tokens=max_new_tokens, do_sample=do_sample)
    if do_sample:
        gen_kwargs["temperature"] = temperature

    start = time.time()
    outputs = model.generate(**inputs, **gen_kwargs)
    elapsed = time.time() - start

    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True
    )
    return response, elapsed


def run_pilot(model_key: str = "qwen2.5-3b", config_path: str = "config.yaml"):
    config = load_config()
    labels = config["labels"]
    model_cfg = next(m for m in config["models"] if m["name"] == model_key)
    model_id = model_cfg["hf_id"]

    print(f"Loading {model_id} ...")
    model, tokenizer = load_model(model_id)
    print("Model loaded.\n")

    df = pd.read_csv(config["paths"]["processed_sample"])
    real_span = df.iloc[0]["text_spans"]
    gold_label = df.iloc[0]["technique"]

    print(f'Test span: "{real_span}"')
    print(f"Gold label: {gold_label}\n")
    print("=" * 60)

    # 1. Greedy decoding for all 4 strategies
    for strategy in config["prompt_strategies"]:
        prompt = build_prompt(strategy, real_span, labels)
        response, elapsed = generate(
            model, tokenizer, prompt, do_sample=False, max_new_tokens=150
        )
        print(f"\n--- {strategy} (greedy, {elapsed:.1f}s) ---")
        print(response)

    # 2. One stochastic sample, to confirm sampling mode works
    print("\n" + "=" * 60)
    prompt = build_prompt("standard", real_span, labels)
    response, elapsed = generate(
        model, tokenizer, prompt, do_sample=True, temperature=0.7, max_new_tokens=150
    )
    print(f"\n--- standard (stochastic, temp=0.7, {elapsed:.1f}s) ---")
    print(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--model", type=str, default="qwen2.5-3b")
    args = parser.parse_args()

    if args.pilot:
        run_pilot(model_key=args.model)
