import os
import json

import mlrun
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    StoppingCriteria,
    StoppingCriteriaList,
    pipeline,
    set_seed,
)

def init_context(context):
    model_id = os.environ["MODEL_ID"]
    cache_dir = os.environ["CACHE_DIR"]

    # Initialize HF models
    tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir)
    lm_model = AutoModelForCausalLM.from_pretrained(model_id, cache_dir=cache_dir)

    # HF text generation pipeline
    pipe = pipeline(
        "text-generation",
        model=lm_model,
        tokenizer=tokenizer,
        max_new_tokens=512,
        device_map="auto"
    )

    setattr(context.user_data, "pipe", pipe)


def invoke_llm(context, event):
    event_json = json.loads(event.body)
    print(f"Received event: {event_json}")