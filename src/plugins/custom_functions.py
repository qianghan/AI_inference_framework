# src/plugins/custom_functions.py

import logging
import cv2
import numpy as np
import tempfile
import os
import io

logger = logging.getLogger("CustomFunctions")


def custom_resize_image(data, size):
    try:
        # Custom resize implementation using BICUBIC interpolation
        import numpy as np
        import cv2
        from PIL import Image
        img_array = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        pil_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        pil_image = pil_image.resize(size, resample=Image.BICUBIC)
        img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes()
    except Exception as e:
        logger.exception(f"Error in custom_resize_image: {e}")
        return None


def custom_enhance_image(data, factor):
    try:
        # Custom enhancement using detail enhancement
        import numpy as np
        import cv2
        img_array = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        img = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)
        img = cv2.convertScaleAbs(img, alpha=factor, beta=0)
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes()
    except Exception as e:
        logger.exception(f"Error in custom_enhance_image: {e}")
        return None


# Update custom functions dictionary
from src.core.utils import custom_functions

custom_functions['custom_resize_image'] = custom_resize_image
custom_functions['custom_enhance_image'] = custom_enhance_image

# src/plugins/custom_functions.py

import logging

logger = logging.getLogger("CustomFunctions")



def video_frame_extraction(data, frame_rate=30):
    """
    Extracts frames from video data at the specified frame rate.

    Parameters:
    - data: The input video data as bytes.
    - frame_rate: The desired frame rate for extraction.

    Returns:
    - A list of frames as bytes.
    """
    try:
        logger.info("Starting video frame extraction.")
        # Write the video data to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(data)
            tmp_filename = tmp_file.name

        cap = cv2.VideoCapture(tmp_filename)

        # Set the desired frame rate
        original_frame_rate = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(max(1, original_frame_rate / frame_rate))

        frames = []
        frame_count = 0
        success, frame = cap.read()
        while success:
            if frame_count % frame_interval == 0:
                # Encode frame to bytes
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                frames.append(frame_bytes)
            success, frame = cap.read()
            frame_count += 1

        cap.release()
        # Remove the temporary file
        os.remove(tmp_filename)

        logger.info(f"Extracted {len(frames)} frames from video.")
        return frames
    except Exception as e:
        logger.exception(f"Error in video_frame_extraction: {e}")
        return None

def video_frame_assembly(frames, frame_rate=30):
    """
    Assembles frames into a video at the specified frame rate.

    Parameters:
    - frames: A list of frames as bytes.
    - frame_rate: The frame rate for the output video.

    Returns:
    - The assembled video data as bytes.
    """
    try:
        logger.info("Starting video frame assembly.")
        if not frames:
            logger.error("No frames provided for assembly.")
            return None

        # Decode the first frame to get frame dimensions
        img_array = np.frombuffer(frames[0], dtype=np.uint8)
        first_frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        height, width, layers = first_frame.shape

        # Create a temporary file for the video
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            video_filename = tmp_file.name

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(video_filename, fourcc, frame_rate, (width, height))

        for frame_bytes in frames:
            img_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if frame is not None:
                video_writer.write(frame)
            else:
                logger.warning("Skipping a frame during assembly due to decoding failure.")

        video_writer.release()

        # Read the video data from the temporary file
        with open(video_filename, 'rb') as f:
            video_data = f.read()

        # Remove the temporary file
        os.remove(video_filename)

        logger.info("Video frame assembly completed.")
        return video_data
    except Exception as e:
        logger.exception(f"Error in video_frame_assembly: {e}")
        return None

# Update custom functions dictionary
from src.core.utils import custom_functions

custom_functions['video_frame_extraction'] = video_frame_extraction
custom_functions['video_frame_assembly'] = video_frame_assembly

# Add any other custom functions here


