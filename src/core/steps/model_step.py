# src/core/steps/model_step.py

import logging
from .base_step import BaseStep
import torch
from diffusers import StableDiffusionImg2ImgPipeline
import numpy as np
import cv2
from PIL import Image

logger = logging.getLogger("ModelStep")


class ModelStep(BaseStep):
    def __init__(self, name, model_name, params):
        super().__init__(name, params)
        self.model_name = model_name
        self.model = self.load_model(model_name)

    @staticmethod
    def from_config(config):
        name = config.get('name')
        model_name = config.get('model_name')
        params = config.get('params', {})
        return ModelStep(name, model_name, params)

    def load_model(self, model_name):
        try:
            logger.info(f"Loading model '{model_name}'...")
            model = StableDiffusionImg2ImgPipeline.from_pretrained(
                model_name, torch_dtype=torch.float16
            )
            model.to("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"Model '{model_name}' loaded successfully.")
            return model
        except Exception as e:
            logger.exception(f"Failed to load model '{model_name}': {e}")
            return None

    def process(self, data):
        if self.model is None:
            logger.error(f"Model '{self.model_name}' is not loaded.")
            return None
        try:
            # Convert data to PIL image
            img_array = np.frombuffer(data, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            init_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            # Perform inference
            with torch.no_grad():
                output = self.model(
                    prompt=self.params.get('prompt', ''),
                    image=init_image
                ).images[0]
            # Convert back to bytes
            output_img = cv2.cvtColor(np.array(output), cv2.COLOR_RGB2BGR)
            _, buffer = cv2.imencode('.jpg', output_img)
            return buffer.tobytes()
        except Exception as e:
            logger.exception(f"Error during model inference in step '{self.name}': {e}")
            return None
