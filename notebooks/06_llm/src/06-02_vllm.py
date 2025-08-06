import json
import os
from time import sleep

import mlrun
import torch
from vllm import LLM, SamplingParams


# def init_context(context: mlrun.MLClientCtx):
#     model_id = os.environ["MODEL_ID"]
#     cache_dir = os.environ["CACHE_DIR"]

#     context.logger.info(f"Initializing vLLM with model {model_id} and cache directory {cache_dir}")
#     print("Initialized")

def test_cuda():
    # setting device on GPU if available, else CPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Using device:', device)
    print()

    #Additional Info when using cuda
    if device.type == 'cuda':
        print(torch.cuda.get_device_name(0))
        print('Memory Usage:')
        print('Allocated:', round(torch.cuda.memory_allocated(0)/1024**3,1), 'GB')
        print('Cached:   ', round(torch.cuda.memory_reserved(0)/1024**3,1), 'GB')

    return f"Device: {device}, Model ID: {os.environ['MODEL_ID']}, Cache Directory: {os.environ['CACHE_DIR']}, GPU Available: {torch.cuda.is_available()}"

def init_model(context: mlrun.MLClientCtx):
    model_id = os.environ["MODEL_ID"]
    cache_dir = os.environ["CACHE_DIR"]

    context.logger.info(f"Initializing vLLM with model {model_id} and cache directory {cache_dir}")
   
    llm = LLM(model=model_id)
    context.logger.info("vLLM initialized successfully")
    
    return llm

def vllm_batch(context: mlrun.MLClientCtx, event):
    #event_json = json.loads(event)
    print(f"Received event: {event}")
    
    # test of cuda is working
    test_result = test_cuda()
    print(test_result)

    # initialize the model
    llm = init_model(context)
    
    return test_result

