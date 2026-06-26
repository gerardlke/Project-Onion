import asyncio
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.logging import setup_logger

logger = setup_logger(__name__)

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

_model = None
_tokenizer = None
_load_lock = asyncio.Lock()


async def _get_model_and_tokenizer():
    """
    Lazily load model + tokenizer on first call, then reuse.
    Wrapped in an asyncio.Lock so concurrent requests arriving before model finishes loading don't each trigger their own separate load.
    """
    global _model, _tokenizer

    if _model is not None:
        return _model, _tokenizer

    async with _load_lock:
        # Re-check inside the lock — another coroutine may have finished
        # loading while we were waiting to acquire it
        if _model is not None:
            return _model, _tokenizer

        logger.info(f"Loading local model '{MODEL_NAME}' — first call only")

        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float32,  # use float16/bfloat16 if you have a GPU
            device_map="auto",          # picks GPU if available, else CPU
        )

        logger.info("Local model loaded")

    return _model, _tokenizer


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

    # Apply the model's own chat template — every instruction-tuned model
    # expects a specific token format (e.g. <|im_start|>user ... <|im_end|>).
    # Getting this wrong silently degrades output quality, so always use
    # the tokenizer's built-in template rather than hand-rolling it.
    encoded = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
    )
    input_ids = encoded.input_ids if hasattr(encoded, "input_ids") else encoded
    input_ids = input_ids.to(model.device)

    # blocking, synchronous, CPU/GPU-bound call -> wrap the generation call in a nested function
    def sync_generate():
        return model.generate(
            input_ids,  # Pass positionally
            max_new_tokens=max_new_tokens,
            do_sample=(temperature > 0.0),
            temperature=temperature if temperature > 0.0 else None,
            pad_token_id=tokenizer.eos_token_id,
            attention_mask=torch.ones_like(input_ids)
        )

    # Offload the wrapper to the thread
    output_ids = await asyncio.to_thread(sync_generate)

    # output_ids includes the input prompt tokens followed by generated tokens.
    # Slice off the input length so we only decode the new tokens.
    new_tokens = output_ids[0][input_ids.shape[-1]:]
    completion = tokenizer.decode(new_tokens, skip_special_tokens=True)

    return completion.strip()