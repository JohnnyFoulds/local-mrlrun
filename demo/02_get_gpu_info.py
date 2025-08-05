
import GPUtil
import subprocess

def get_gpu_info(context):    
    gpus = GPUtil.getGPUs()
    gpu_info = []
    for gpu in gpus:
        gpu_info.append({
            'id': gpu.id,
            'name': gpu.name,
            'load': gpu.load,
            'memory_total': gpu.memoryTotal,
            'memory_free': gpu.memoryFree,
            'memory_used': gpu.memoryUsed,
        })

    print(f"GPU Info v4: {gpu_info}")
    context.logger.info(f"GPU Info: {gpu_info}")

    # execute the nvidia-smi command on the cli to get detailed GPU info
    try:
        nvidia_smi_output = subprocess.check_output(['nvidia-smi'], universal_newlines=True)
        print("NVIDIA-SMI Output:")
        print(nvidia_smi_output)
        context.logger.info(f"NVIDIA-SMI Output:\n{nvidia_smi_output}")
    except Exception as e:
        error_msg = f"Error running nvidia-smi: {str(e)}"
        print(error_msg)
        context.logger.warning(error_msg)
    
    return gpu_info
