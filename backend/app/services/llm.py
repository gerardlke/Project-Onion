import asyncio
import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer

### Set up configs
from app.configs.config import LLM

### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)


_model = None
_tokenizer = None
_load_lock = asyncio.Lock()


async def _get_model_and_tokenizer():
    """Lazily load model + tokenizer on first call, then reuse"""
    global _model, _tokenizer

    if _model is not None:
        return _model, _tokenizer

    async with _load_lock:
        if _model is not None:
            return _model, _tokenizer

        logger.info(f"Loading local model '{LLM}'")

        _tokenizer = AutoTokenizer.from_pretrained(LLM)
        _model = AutoModelForCausalLM.from_pretrained(
            LLM,
            torch_dtype=torch.float32,
            device_map="auto",  # picks GPU if available, else CPU
        )

        logger.info("Local model loaded")

    return _model, _tokenizer


async def llm_warm_up():
    """Pre-load the LLM into memory during application startup before first call"""
    logger.info("Warming up LLM...")
    await _get_model_and_tokenizer()
    logger.info("LLM warm-up complete")


async def generate(prompt: str, max_new_tokens: int = 1000, temperature: float = 0.0):
    """Generate a completion for a single user prompt.

    Input:
    - prompt:           The full prompt text (already formatted, e.g. via CONCEPT_EXTRACTION_PROMPT.format(...))
    - max_new_tokens:   Generation budget — mirrors max_tokens in the OpenAI API
    - temperature:      0.0 = deterministic (greedy decoding)

    Output: Decoded string completion (model's reply only, prompt stripped out)
    """
    model, tokenizer = await _get_model_and_tokenizer()

    messages = [{"role": "user", "content": prompt}]

    # Apply the model's own chat template
    encoded = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
    )
    input_ids = encoded.input_ids if hasattr(encoded, "input_ids") else encoded
    input_ids = input_ids.to(model.device)

    # blocking, synchronous, CPU/GPU-bound call -> wrap generation call in a nested function
    def sync_generate():
        start = time.time()
        res = model.generate(
            input_ids,  # Pass positionally
            max_new_tokens=max_new_tokens,
            do_sample=(temperature > 0.0),
            temperature=temperature if temperature > 0.0 else None,
            pad_token_id=tokenizer.eos_token_id,
            attention_mask=torch.ones_like(input_ids)
        )
        logger.info(f"Time taken for LLM generation: {round(time.time() - start)}s")
        return res

    # Offload wrapper to thread
    output_ids = await asyncio.to_thread(sync_generate)

    new_tokens = output_ids[0][input_ids.shape[-1]:]
    completion = tokenizer.decode(new_tokens, skip_special_tokens=True)

    return completion.strip()