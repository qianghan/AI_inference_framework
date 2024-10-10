# src/core/steps/base_step.py

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger("BaseStep")


class BaseStep(ABC):
    def __init__(self, name, params, is_async=False):
        self.name = name
        self.params = params
        self.is_async = is_async

    @abstractmethod
    def process(self, data):
        pass


class StepFactory:
    @staticmethod
    def create_step(step_config):
        try:
            step_type = step_config.get('type')
            if step_type == 'function':
                from .function_step import FunctionStep
                step = FunctionStep.from_config(step_config)
                logger.info(f"Created FunctionStep: {step.name}")
                return step
            elif step_type == 'model':
                model_name = step_config.get('model_name')
                if model_name == 'custom_livediff_model':
                    from src.plugins.custom_models import CustomLiveDiffModelStep
                    step = CustomLiveDiffModelStep.from_config(step_config)
                    logger.info(f"Created CustomLiveDiffModelStep: {step.name}")
                    return step
                elif model_name == 'custom_lora_model':
                    from src.plugins.custom_models import CustomLoRAModelStep
                    step = CustomLoRAModelStep.from_config(step_config)
                    logger.info(f"Created CustomLoRAModelStep: {step.name}")
                    return step
                else:
                    from .model_step import ModelStep
                    step = ModelStep.from_config(step_config)
                    logger.info(f"Created ModelStep: {step.name}")
                    return step
            else:
                logger.error(f"Invalid step type: {step_type}")
                return None
        except Exception as e:
            logger.exception(f"Error creating step from config: {step_config}, Error: {e}")
            return None
