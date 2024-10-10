# src/services/whep_playback_server.py

import asyncio
import logging
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.mediastreams import VideoFrame
from ray import serve
import cv2
import numpy as np

logger = logging.getLogger("WHEPPlaybackServer")


@serve.deployment(route_prefix="/whep_playback")
@serve.ingress(web.Application)
class WHEPPlaybackServer:
    def __init__(self, output_buffer):
        self.pcs = set()
        self.output_buffer = output_buffer

    @web.post("/")
    async def playback(self, request):
        try:
            params = await request.json()
            offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        except Exception as e:
            logger.error(f"Invalid request data: {e}")
            return web.Response(text="Invalid request data.", status=400)

        pc = RTCPeerConnection()
        self.pcs.add(pc)

        @pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            try:
                state = pc.iceConnectionState
                logger.info(f"ICE connection state is {state}")
                if state == "failed":
                    await pc.close()
                    self.pcs.discard(pc)
            except Exception as e:
                logger.exception(f"Error in ICE connection state change handler: {e}")

        # Add the output video track
        local_video = ProcessedVideoTrack(self.output_buffer)
        pc.addTrack(local_video)

        try:
            await pc.setRemoteDescription(offer)
            await pc.setLocalDescription(await pc.createAnswer())
        except Exception as e:
            logger.exception(f"Error during WebRTC handshake: {e}")
            return web.Response(text="Error during WebRTC handshake.", status=500)

        return web.json_response(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        )

    async def on_shutdown(self):
        coros = [pc.close() for pc in self.pcs]
        await asyncio.gather(*coros)
        self.pcs.clear()


class ProcessedVideoTrack(VideoStreamTrack):
    def __init__(self, output_buffer):
        super().__init__()
        self.output_buffer = output_buffer

    async def recv(self):
        while True:
            try:
                # Get processed frame from output buffer
                frame_bytes = await self.output_buffer.get_frame.remote()
                if frame_bytes is not None:
                    # Convert bytes to image
                    img_array = np.frombuffer(frame_bytes, dtype=np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    # Create VideoFrame
                    new_frame = VideoFrame.from_ndarray(img, format="bgr24")
                    new_frame.pts = None
                    new_frame.time_base = None
                    return new_frame
                else:
                    # If no frame is available, wait briefly
                    await asyncio.sleep(0.01)
            except Exception as e:
                logger.exception(f"Error in ProcessedVideoTrack recv: {e}")
                await asyncio.sleep(0.01)
