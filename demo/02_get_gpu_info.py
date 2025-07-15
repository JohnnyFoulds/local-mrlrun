
import GPUtil

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

    context.logger.info(f"GPU Info: {gpu_info}")
    return gpu_info
