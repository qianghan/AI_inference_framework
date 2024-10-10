# sdk/pipeline_client.py

import requests
import yaml
import os
import logging

logger = logging.getLogger("PipelineClient")


class PipelineClient:
    def __init__(self, server_url='http://localhost:8000'):
        self.server_url = server_url.rstrip('/')

    def set_pipeline(self, pipeline_config):
        try:
            if isinstance(pipeline_config, dict):
                pipeline_yaml = yaml.dump(pipeline_config)
            elif isinstance(pipeline_config, str):
                if os.path.exists(pipeline_config):
                    with open(pipeline_config, 'r') as f:
                        pipeline_yaml = f.read()
                else:
                    pipeline_yaml = pipeline_config
            else:
                raise ValueError("pipeline_config must be a YAML string, a file path, or a dictionary.")

            url = f"{self.server_url}/pipeline?action=set_pipeline"
            headers = {'Content-Type': 'text/plain'}

            response = requests.post(url, data=pipeline_yaml, headers=headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.exception(f"Error in set_pipeline: {e}")
            raise

    def upload_custom_functions(self, file_path):
        try:
            url = f"{self.server_url}/pipeline?action=upload_function"

            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                response = requests.post(url, files=files)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.exception(f"Error in upload_custom_functions: {e}")
            raise

    def list_functions(self):
        try:
            url = f"{self.server_url}/pipeline?action=list_functions"

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get('custom_functions', [])
        except Exception as e:
            logger.exception(f"Error in list_functions: {e}")
            raise

    def get_pipeline(self):
        try:
            url = f"{self.server_url}/pipeline?action=get_pipeline"

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get('pipeline', {})
        except Exception as e:
            logger.exception(f"Error in get_pipeline: {e}")
            raise

    def infer(self, data):
        try:
            url = f"{self.server_url}/pipeline?action=inference"
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.exception(f"Error in infer: {e}")
            raise
