
FROM dragon:30500/mlrun/mlrun:1.9.1

RUN pip install --upgrade pip \
 && pip install --no-cache-dir --force-reinstall \
      numpy==1.26.4 \
      pandas==2.1.4 \
      mlrun==1.9.1 \
      vllm==0.10.0 
      
# RUN pip install --no-cache-dir \
#     torch==2.7.1 \
#     torchvision==2.7.1 \
#     torchaudio==0.22.1 \
#     --index-url https://download.pytorch.org/whl/cu124
    
# RUN pip install --no-cache-dir \
#     vllm==0.10.0 

RUN touch /tmp/.vllm_ready
