# src/core/pipeline.py

import logging
import yaml
from .steps.base_step import StepFactory

logger = logging.getLogger("Pipeline")


class Pipeline:
    def __init__(self):
        self.steps = []
        self.pipeline_config = {}

    def configure(self, config_path):
        try:
            with open(config_path, 'r') as f:
                pipeline_config = yaml.safe_load(f)
            self.configure_from_dict(pipeline_config)
            logger.info(f"Pipeline configured from {config_path}")
        except Exception as e:
            logger.error(f"Failed to configure pipeline from {config_path}: {e}")
            raise

    def configure_from_string(self, config_str):
        try:
            pipeline_config = yaml.safe_load(config_str)
            self.configure_from_dict(pipeline_config)
            logger.info("Pipeline configured from string")
        except Exception as e:
            logger.error(f"Failed to configure pipeline from string: {e}")
            raise

    def configure_from_dict(self, pipeline_config):
        try:
            self.pipeline_config = pipeline_config
            steps_config = pipeline_config.get('steps', [])
            self.steps = []
            for step_config in steps_config:
                step = StepFactory.create_step(step_config)
                if step:
                    self.steps.append(step)
                else:
                    logger.error(f"Failed to create step from config: {step_config}")
                    raise ValueError(f"Invalid step configuration: {step_config}")
        except Exception as e:
            logger.error(f"Error configuring pipeline from dict: {e}")
            raise

    def get_pipeline_config(self):
        return self.pipeline_config
