import mlrun
from huggingface_hub import snapshot_download

class VLLMModelServer(mlrun.serving.v2_serving.V2ModelServer):
    """
    A model server for VLLM models, inheriting from VisionModelServer.
    This class is designed to handle VLLM models specifically, including
    loading, serving, and managing their lifecycle.
    """
    def __init__(
        self,
        context: mlrun.MLClientCtx,
        name: str,
        model_path: str,
        model_name: str,
        **class_args
    ):
        """
        Initialize the VLLMModelServer with the given context, name, model path, and model name.

        :param context: MLRun context for the server.
        :param name: Name of the model server.
        :param model_path: Path to the VLLM model.
        :param model_name: Name of the VLLM model.
        :param class_args: Additional arguments for the model server.
        """
        super().__init__(
            context=context,
            name=name,
            model_path=model_path,
            **class_args
        )

        # Save hub loading parameters:
        self.model_name = model_name