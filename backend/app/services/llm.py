import os
import time
import torch
import asyncio
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer
from openai import AsyncOpenAI

### Set up configs
from app.configs.config import (
    LOCAL_DEPLOYMENT, 
    LOCAL_LLM,
    API_LLM
)

### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)

load_dotenv()

# Groq API 
groq_client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Local model state
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

        logger.info(f"Loading local model '{LOCAL_LLM}'")

        _tokenizer = AutoTokenizer.from_pretrained(LOCAL_LLM)
        _model = AutoModelForCausalLM.from_pretrained(
            LOCAL_LLM,
            torch_dtype=torch.float32,
            device_map="auto",  # picks GPU if available, else CPU
        )

        logger.info("Local model loaded")
    return _model, _tokenizer


async def llm_warm_up():
    """Pre-load the LLM into memory during application startup before first call"""
    if LOCAL_DEPLOYMENT:
        logger.info("Warming up local LLM...")
        await _get_model_and_tokenizer()
    else:
        logger.info("Using LLM API. No warm up needed.")


async def local_generate(messages, max_new_tokens, temperature):
    """Generates llm response using locally deployed llm"""
    try:
        model, tokenizer = await _get_model_and_tokenizer()
        encoded = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(model.device)
        
        def sync_generate():
            output = model.generate(
                encoded,
                max_new_tokens=max_new_tokens,
                do_sample=(temperature > 0.0),
                temperature=temperature if temperature > 0.0 else None,
                pad_token_id=tokenizer.eos_token_id
            )
            return output[0][encoded.shape[-1]:]

        output_tokens = await asyncio.to_thread(sync_generate)
        return tokenizer.decode(output_tokens, skip_special_tokens=True).strip()
    except Exception as e:
        logger.error(f"Local llm error: {e}")
        return "Error generatoing response via local LLM."


async def api_generate(messages, max_new_tokens, temperature):
    """Generates llm response using llm api"""
    try:
        response = await groq_client.chat.completions.create(
            model=API_LLM,
            messages=messages,
            max_tokens=max_new_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq API Error: {e}")
        return "Error generating response via API."


async def generate(prompt: str = None, messages: list[dict] = None, max_new_tokens: int = 1000, temperature: float = 0.0):
    """Generate a completion for a single user prompt either via local LLM or API

    Input:
    - prompt:           The full prompt text (already formatted, e.g. via CONCEPT_EXTRACTION_PROMPT.format(...))
    - max_new_tokens:   Generation budget — mirrors max_tokens in the OpenAI API
    - temperature:      0.0 = deterministic (greedy decoding)

    Output: Decoded string completion (model's reply only, prompt stripped out)
    """
    if prompt is None and messages is None:
        raise ValueError("Either prompt or messages must be passed into LLM")
     
    if messages is None:
        messages = [{"role": "user", "content": prompt}]
    
    start = time.time()

    if LOCAL_DEPLOYMENT:
        res = await local_generate(messages, max_new_tokens, temperature)
    else:
        res = await api_generate(messages, max_new_tokens, temperature)

    logger.info(f"LLM generation completed in {round(time.time() - start)}s")
    return res