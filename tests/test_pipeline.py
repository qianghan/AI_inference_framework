# tests/test_pipeline.py

import unittest
from sdk.pipeline_client import PipelineClient
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestPipeline")


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.client = PipelineClient()

    def test_set_pipeline(self):
        # Define a simple pipeline configuration
        pipeline_config = {
            'pipeline_name': 'test_pipeline',
            'steps': [
                {
                    'name': 'resize',
                    'type': 'function',
                    'function': 'resize_image',
                    'params': {
                        'size': [512, 512]
                    }
                },
                {
                    'name': 'enhance',
                    'type': 'function',
                    'function': 'enhance_image',
                    'params': {
                        'factor': 1.1
                    }
                }
            ]
        }

        # Set the pipeline
        response = self.client.set_pipeline(pipeline_config)
        self.assertIn("Pipeline set successfully", response)

    def test_upload_custom_functions(self):
        # Assuming 'custom_functions.py' exists in 'src/plugins'
        custom_functions_path = 'src/plugins/custom_functions.py'
        if os.path.exists(custom_functions_path):
            response = self.client.upload_custom_functions(custom_functions_path)
            self.assertIn("Functions uploaded successfully", response)
        else:
            self.skipTest(f"{custom_functions_path} does not exist.")

    def test_get_pipeline(self):
        pipeline = self.client.get_pipeline()
        self.assertIsInstance(pipeline, dict)
        self.assertIn('pipeline_name', pipeline)

    def test_infer(self):
        # Perform inference on a sample image
        sample_image_path = 'tests/sample_image.jpg'
        if os.path.exists(sample_image_path):
            with open(sample_image_path, 'rb') as f:
                data = f.read()

            result = self.client.infer(data)
            self.assertIsNotNone(result)
            # Save the result to verify manually if needed
            with open('tests/output_image.jpg', 'wb') as f:
                f.write(result)
        else:
            self.skipTest(f"{sample_image_path} does not exist.")


if __name__ == '__main__':
    unittest.main()
