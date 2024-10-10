# src/core/steps/function_step.py

import logging
from .base_step import BaseStep
from ..utils import default_functions, custom_functions

logger = logging.getLogger("FunctionStep")


class FunctionStep(BaseStep):
    def __init__(self, name, function_name, params):
        super().__init__(name, params)
        self.function_name = function_name
        self.function = self.load_function(function_name)

    @staticmethod
    def from_config(config):
        name = config.get('name')
        function_name = config.get('function')
        params = config.get('params', {})
        return FunctionStep(name, function_name, params)

    def load_function(self, function_name):
        if function_name in custom_functions:
            logger.info(f"Using custom function '{function_name}'")
            return custom_functions[function_name]
        elif function_name in default_functions:
            logger.info(f"Using default function '{function_name}'")
            return default_functions.get(function_name)
        else:
            logger.error(f"Function '{function_name}' not found in default or custom functions.")
            return None

    def process(self, data):
        if self.function is None:
            logger.error(f"Function '{self.function_name}' is not loaded.")
            return None
        try:
            result = self.function(data, **self.params)
            return result
        except Exception as e:
            logger.exception(f"Error processing function '{self.function_name}': {e}")
            return None
