# src/services/rtmp_ingest_server.py

import asyncio
import logging
import av
import ray
from ray import serve
from aiohttp import web
from src.core.utils import FrameBuffer
import io

logger = logging.getLogger("RTMPIngestServer")


@serve.deployment(route_prefix="/rtmp_ingest")
@serve.ingress(web.Application)
class RTMPIngestServer:
    def __init__(self, input_buffer, output_buffer):
        self.input_buffer = input_buffer
        self.output_buffer = output_buffer

    @web.post("/")
    async def ingest(self, request):
        try:
            params = await request.json()
            stream_url = params.get("stream_url")
            if not stream_url:
                logger.error("No stream URL provided.")
                return web.Response(text="No stream URL provided.", status=400)
        except Exception as e:
            logger.error(f"Invalid request data: {e}")
            return web.Response(text="Invalid request data.", status=400)

        asyncio.create_task(self._process_stream(stream_url))
        return web.Response(text="RTMP stream ingestion started.")

    async def _process_stream(self, stream_url):
        try:
            container = av.open(stream_url)
            for frame in container.decode(video=0):
                img = frame.to_image()
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                frame_bytes = img_byte_arr.getvalue()

                pipeline_available = await self.input_buffer.pipeline_available.remote()
                if pipeline_available:
                    await self.input_buffer.add_frame.remote(frame_bytes)
                else:
                    await self.output_buffer.add_frame.remote(frame_bytes)
        except Exception as e:
            logger.exception(f"Error processing RTMP stream '{stream_url}': {e}")
