
FROM dragon:30500/mlrun/mlrun:1.9.1

RUN pip install --no-cache-dir \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 && \
    pip install --no-cache-dir \
    vllm==0.10.0

RUN touch /tmp/.vllm_ready
