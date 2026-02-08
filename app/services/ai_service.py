from typing import Any, List
import asyncio
from concurrent.futures import ThreadPoolExecutor

# We will use lazy loading to avoid loading model at startup if not needed.
# This prevents huge memory usage if the endpoint isn't hit.
_model = None
_tokenizer = None
_executor = ThreadPoolExecutor(max_workers=1)

import os

def load_model():
    global _model, _tokenizer
    if os.getenv("MOCK_AI_MODEL", "false").lower() == "true":
        print("Mock AI Model Enabled. Skipping load.")
        return

    if _model is None:
        print("Loading AI Model (distilgpt2)...")
        from transformers import AutoModelForCausalLM, AutoTokenizer
        # Use a small model for local testing
        model_name = "distilgpt2" 
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = AutoModelForCausalLM.from_pretrained(model_name)
        print("AI Model Loaded.")

def generate_text_sync(prompt: str, max_length: int = 50) -> str:
    load_model()
    
    if os.getenv("MOCK_AI_MODEL", "false").lower() == "true":
        return f"[MOCK AI] Generated text for: {prompt}"

    inputs = _tokenizer.encode(prompt, return_tensors="pt")
    outputs = _model.generate(
        inputs, 
        max_length=max_length, 
        num_return_sequences=1,
        pad_token_id=_tokenizer.eos_token_id,
        do_sample=True,
        temperature=0.7
    )
    return _tokenizer.decode(outputs[0], skip_special_tokens=True)

async def generate_text(prompt: str, max_length: int = 50) -> str:
    # Run blocking CPU-bound model inference in a thread
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_executor, generate_text_sync, prompt, max_length)
