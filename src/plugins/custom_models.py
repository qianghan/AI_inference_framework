# src/plugins/custom_models.py

import logging
from src.core.steps.base_step import BaseStep
import torch
from diffusers import StableDiffusionPipeline
import numpy as np
import cv2
from PIL import Image

logger = logging.getLogger("CustomModels")


class CustomLiveDiffModelStep(BaseStep):
    def __init__(self, name, model_name, params):
        super().__init__(name, params)
        self.model_name = model_name
        self.model = self.load_model(model_name)

    @staticmethod
    def from_config(config):
        name = config.get('name')
        model_name = config.get('model_name')
        params = config.get('params', {})
        return CustomLiveDiffModelStep(name, model_name, params)

    def load_model(self, model_name):
        try:
            logger.info(f"Loading LiveDiff model '{model_name}'...")
            # Implement the model loading logic specific to LiveDiff
            # For example, if LiveDiff uses a specific pipeline or custom code
            # Replace the following line with the actual model loading code

            # Placeholder: Using StableDiffusionPipeline as an example
            model = StableDiffusionPipeline.from_pretrained(
                model_name, torch_dtype=torch.float16
            )
            model.to("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"LiveDiff model '{model_name}' loaded successfully.")
            return model
        except Exception as e:
            logger.exception(f"Failed to load LiveDiff model '{model_name}': {e}")
            return None

    def process(self, data):
        if self.model is None:
            logger.error(f"LiveDiff model '{self.model_name}' is not loaded.")
            return None
        try:
            # Convert data to PIL image
            img_array = np.frombuffer(data, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            input_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

            # Perform inference with LiveDiff
            # Implement the specific inference logic for LiveDiff
            # Placeholder: Using the model as if it's a standard StableDiffusionPipeline
            with torch.no_grad():
                output = self.model(
                    prompt=self.params.get('prompt', ''),
                    image=input_image
                ).images[0]

            # Convert back to bytes
            output_img = cv2.cvtColor(np.array(output), cv2.COLOR_RGB2BGR)
            _, buffer = cv2.imencode('.jpg', output_img)
            return buffer.tobytes()
        except Exception as e:
            logger.exception(f"Error during LiveDiff model inference in step '{self.name}': {e}")
            return None


class CustomLoRAModelStep(BaseStep):
    def __init__(self, name, model_name, params):
        super().__init__(name, params)
        self.model_name = model_name
        self.model = self.load_model()

    @staticmethod
    def from_config(config):
        name = config.get('name')
        model_name = config.get('model_name')
        params = config.get('params', {})
        return CustomLoRAModelStep(name, model_name, params)

    def load_model(self):
        try:
            logger.info(f"Loading LoRA model '{self.model_name}'...")
            base_model_name = self.params.get('base_model', 'stabilityai/stable-diffusion-2-1-base')
            lora_weights_path = self.params.get('lora_weights_path')

            if not lora_weights_path:
                logger.error("LoRA weights path not provided in parameters.")
                return None

            # Load the base model
            model = StableDiffusionPipeline.from_pretrained(
                base_model_name, torch_dtype=torch.float16
            )
            model.to("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"Base model '{base_model_name}' loaded successfully.")

            # Load LoRA weights
            # Implement LoRA weights loading
            # Placeholder: Assuming use of `diffusers.load_lora_weights`
            from diffusers.utils import load_lora_weights
            model = load_lora_weights(model, lora_weights_path)
            logger.info(f"LoRA weights from '{lora_weights_path}' loaded successfully.")

            return model
        except Exception as e:
            logger.exception(f"Failed to load LoRA model '{self.model_name}': {e}")
            return None

    def process(self, data):
        if self.model is None:
            logger.error(f"LoRA model '{self.model_name}' is not loaded.")
            return None
        try:
            # Convert data to PIL image
            img_array = np.frombuffer(data, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            input_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

            # Perform inference with the LoRA model
            with torch.no_grad():
                output = self.model(
                    prompt=self.params.get('prompt', ''),
                    image=input_image
                ).images[0]

            # Convert back to bytes
            output_img = cv2.cvtColor(np.array(output), cv2.COLOR_RGB2BGR)
            _, buffer = cv2.imencode('.jpg', output_img)
            return buffer.tobytes()
        except Exception as e:
            logger.exception(f"Error during LoRA model inference in step '{self.name}': {e}")
            return None

# Update StepFactory to recognize custom models
from src.core.steps.base_step import StepFactory

StepFactory.register_custom_model('custom_livediff_model', CustomLiveDiffModelStep)
StepFactory.register_custom_model('custom_lora_model', CustomLoRAModelStep)
