# src/core/utils.py

import cv2
import numpy as np
from PIL import Image
import ray
import logging

logger = logging.getLogger("Utils")


@ray.remote
class FrameBuffer:
    def __init__(self, max_length=100):
        self.frames = []
        self.max_length = max_length
        self.pipeline_available_flag = False

    async def add_frame(self, frame):
        if len(self.frames) >= self.max_length:
            logger.warning("FrameBuffer is full. Dropping frame.")
            return
        self.frames.append(frame)
        logger.debug("Frame added to buffer.")

    async def get_frame(self):
        if self.frames:
            frame = self.frames.pop(0)
            logger.debug("Frame retrieved from buffer.")
            return frame
        else:
            return None

    async def pipeline_available(self):
        return self.pipeline_available_flag

    async def set_pipeline_available(self, available: bool):
        self.pipeline_available_flag = available


def resize_image(data, size):
    try:
        img_array = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        pil_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        pil_image = pil_image.resize(size)
        img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes()
    except Exception as e:
        logger.exception(f"Error in resize_image: {e}")
        return None


def enhance_image(data, factor):
    try:
        img_array = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        img = cv2.convertScaleAbs(img, alpha=factor, beta=0)
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes()
    except Exception as e:
        logger.exception(f"Error in enhance_image: {e}")
        return None


default_functions = {
    'resize_image': resize_image,
    'enhance_image': enhance_image,
}

custom_functions = {}
