import os
import shutil
import mlrun
from mlrun.projects.project import MlrunProject
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

    def _download_model(self):
        """
        Download the model from Hugging Face Hub if it is not already present.
        """
        self.context.logger.info(f"Downloading model {self.model_name} to {self.model_path}")
        
        snapshot_download(
            repo_id=self.model_name,
            local_dir=self.model_path)

        # delete the .cache directory if it exists
        cache_dir = os.path.join(self.model_path, ".cache")
        if os.path.exists(cache_dir):
            self.context.logger.info(f"Deleting cache directory: {cache_dir}")
            shutil.rmtree(cache_dir)
        
        self.context.logger.info(f"Model {self.model_name} downloaded successfully to: {self.model_path}")

    def _log_model(self):
        """
        Log the model to the MLRun project.

        :param project: The MLRun project to log the model to.
        """
        # get the project from the context
        project_name = self.context.project
        project = mlrun.get_or_create_project(name=project_name)
        
        self.context.logger.info(f"Logging model {self.model_name} to project {project.name}")
        
        # Assuming the model is saved in the model_path
        model_artifact = project.log_artifact(
           item=self.name, 
           local_path=self.model_path,
           upload=True,
           labels={"framework": "vllm", "source": "huggingface"}
        )
        # model_artifact = project.log_model(
        #     key=self.name,
        #      model_dir=self.model_path,
        #     labels={"framework": "vllm", "source": "huggingface"}
        # )
        
        self.context.logger.info(f"Model {self.model_name} logged successfully to: {model_artifact.uri}")

    def store_model(self):
        """
        Store the model in the MLRun project.
        This method is called to ensure the model is stored correctly.
        """
        self.context.logger.info(f"Storing model {self.model_name} in project {self.context.project}")
        
        # Download the model
        self._download_model()
        
        # Log the model to the project
        self._log_model()   

        # Delete the local model files after logging
        if os.path.exists(self.model_path):
            self.context.logger.info(f"Deleting local model files at {self.model_path}")
            shutil.rmtree(self.model_path)
        
        self.context.logger.info(f"Model {self.model_name} stored successfully.")