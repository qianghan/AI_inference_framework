# src/core/engine.py

import asyncio
import logging
from .pipeline import Pipeline
from .utils import FrameBuffer
import ray
from ray import serve

logger = logging.getLogger("Engine")


@serve.deployment
class Engine:
    def __init__(self, config_path):
        self.pipeline = Pipeline()
        self.config_path = config_path

        # Load default pipeline
        self.load_pipeline(config_path)

        # Initialize frame buffers as Ray actors
        self.input_buffer = FrameBuffer.options(name="input_buffer").remote()
        self.output_buffer = FrameBuffer.options(name="output_buffer").remote()

        # Start processing task
        self.processing_task = asyncio.create_task(self.process_frames())

    def load_pipeline(self, config_path):
        try:
            self.pipeline.configure(config_path)
            logger.info(f"Pipeline loaded from {config_path}")
        except Exception as e:
            logger.exception(f"Failed to load pipeline from {config_path}: {e}")

    def load_pipeline_from_string(self, pipeline_config_str):
        try:
            self.pipeline.configure_from_string(pipeline_config_str)
            logger.info("Pipeline loaded from string.")
        except Exception as e:
            logger.exception(f"Failed to load pipeline from string: {e}")

    async def process_frames(self):
        logger.info("Starting frame processing loop.")
        while True:
            try:
                frame = await self.input_buffer.get_frame.remote()
                if frame is not None:
                    processed_frame = await self.process_frame(frame)
                    if processed_frame:
                        await self.output_buffer.add_frame.remote(processed_frame)
                else:
                    # Sleep briefly if no frame is available
                    await asyncio.sleep(0.01)
            except Exception as e:
                logger.exception(f"Error in process_frames: {e}")
                await asyncio.sleep(0.1)

    async def process_frame(self, frame):
        if not self.pipeline.steps:
            logger.warning("No pipeline is currently loaded.")
            return None
        data = frame
        for step in self.pipeline.steps:
            try:
                if asyncio.iscoroutinefunction(step.process):
                    data = await step.process(data)
                else:
                    # Use Ray tasks to run synchronous steps
                    data = await ray.remote(step.process).remote(data)
                if data is None:
                    logger.error(f"Step '{step.name}' returned None.")
                    return None
            except Exception as e:
                logger.exception(f"Error during pipeline execution at step '{step.name}': {e}")
                return None
        return data

    async def __call__(self, request):
        action = request.query.get("action")
        if action == "set_pipeline":
            pipeline_config = await request.text()
            self.load_pipeline_from_string(pipeline_config)
            return serve.Response("Pipeline set successfully.", status=200)
        elif action == "get_pipeline":
            pipeline = self.pipeline.get_pipeline_config()
            return serve.json_response({"pipeline": pipeline})
        else:
            return serve.Response("Invalid action.", status=400)
