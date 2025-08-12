import os
import shutil
import tempfile
from typing import Dict, List, Optional, Union

import mlrun
from mlrun.projects.project import MlrunProject
from huggingface_hub import snapshot_download
from vllm import LLM, RequestOutput, SamplingParams


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

    #region Model Management
    def _download_model(self):
        """
        Download the model from Hugging Face Hub if it is not already present.
        """
        self.context.logger.info(
            f"Downloading model {self.model_name} to {self.model_path}")

        snapshot_download(
            repo_id=self.model_name,
            local_dir=self.model_path)

        # delete the .cache directory if it exists
        cache_dir = os.path.join(self.model_path, ".cache")
        if os.path.exists(cache_dir):
            self.context.logger.info(f"Deleting cache directory: {cache_dir}")
            shutil.rmtree(cache_dir)

        self.context.logger.info(
            f"Model {self.model_name} downloaded successfully to: {self.model_path}")

    def _log_model(self):
        """
        Log the model to the MLRun project.

        :param project: The MLRun project to log the model to.
        """
        # get the project from the context
        project_name = self.context.project
        project = mlrun.get_or_create_project(name=project_name)

        self.context.logger.info(
            f"Logging model {self.model_name} to project {project.name}")

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

        self.context.logger.info(
            f"Model {self.model_name} logged successfully to: {model_artifact.uri}")

    def store_model(self):
        """
        Store the model in the MLRun project.
        This method is called to ensure the model is stored correctly.
        """
        self.context.logger.info(
            f"Storing model {self.model_name} in project {self.context.project}")

        # Download the model
        self._download_model()

        # Log the model to the project
        self._log_model()

        # Delete the local model files after logging
        if os.path.exists(self.model_path):
            self.context.logger.info(
                f"Deleting local model files at {self.model_path}")
            shutil.rmtree(self.model_path)

        self.context.logger.info(
            f"Model {self.model_name} stored successfully.")
    #endregion Model Management

    def get_model_artifact(self):
        """ Retrieve the model artifact from the MLRun project."""
        project = mlrun.get_or_create_project(name=self.context.project)
        model_artifact = project.get_artifact(self.name)
        return model_artifact

    def _download_tokenizer(self) -> str:
        """
        Download the tokenizer from the model data item.
        """
        # tokenizer files normally needed:
        tokenizer_files = [
            "tokenizer.json",
            "tokenizer.model",         # some models have one or the other
            "tokenizer_config.json",
            "special_tokens_map.json",
            "config.json",              # often needed too
            "generation_config.json",   # optional, if exists
        ]
        
        # create a temporary directory to store the tokenizer files
        temp_dir = tempfile.mkdtemp(prefix="vllm_tokenizer_")
        self.context.logger.info(
            f"Downloading tokenizer files to temporary directory: {temp_dir}")
        
        # get the model artifact from the context
        model_artifact = self.get_model_artifact()

        # get the files in the data item
        data_item = mlrun.get_dataitem(model_artifact.uri)
        data_item_files = data_item.listdir()

        # download tokenizer-related files
        for filename in data_item_files:
            # if the file is not in the tokenizer files, skip it
            if filename not in tokenizer_files:
                continue
            
            # download the file to the temporary directory
            self.context.logger.info(f"..Downloading {filename} to {temp_dir}")
            data_item_file = mlrun.get_dataitem(f"{data_item.url}{filename}")
            data_item_file.download(target_path=f"{temp_dir}/{filename}")

        return temp_dir

    def offline_inference(
        self, 
        prompts:List[str],
        sampling_params: Union[SamplingParams, Dict],
        **generate_kwargs
    ) -> List[RequestOutput]:
        """
        Perform offline inference using the VLLM model.

        :param prompts: List of prompts to process.
        :param sampling_params: Sampling parameters for the model.
        :param generate_kwargs: Additional keyword arguments to pass to llm.generate().
        :return: List of RequestOutput containing the model's responses.
        """
        self.context.logger.info(
            f"Running offline inference...")

        # get the model artifact
        model_artifact = self.get_model_artifact()

        # download the tokenizer
        self.context.logger.info(
            f"Downloading tokenizer for model {self.model_name}")
        tokenizer_dir = self._download_tokenizer()

        # If sampling_params is a dict, convert it to SamplingParams
        if isinstance(sampling_params, dict):
            sampling_params = SamplingParams(**sampling_params)

        # Initialize the LLM with the model path
        llm = LLM(
            model=model_artifact.target_path,
            tokenizer=tokenizer_dir,
            hf_config_path=tokenizer_dir,
            trust_remote_code=True,
            load_format="runai_streamer",
        )

        # Run inference
        outputs = llm.generate(
            prompts,
            sampling_params=sampling_params,
            **generate_kwargs)

        self.context.logger.info(
            f"Offline inference completed with {len(outputs)} responses.")

        return outputs
