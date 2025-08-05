import json
import os

import mlrun
from vllm import LLM, SamplingParams


def init_context(context: mlrun.MLClientCtx):
    model_id = os.environ["MODEL_ID"]
    cache_dir = os.environ["CACHE_DIR"]

    context.logger.info(f"Initializing vLLM with model {model_id} and cache directory {cache_dir}")

def vllm_batch(context: mlrun.MLClientCtx, event):
    #event_json = json.loads(event)
    print(f"Received event: {event}")