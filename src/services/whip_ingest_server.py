# src/services/whip_ingest_server.py

import asyncio
import logging
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay
from ray import serve
from src.core.utils import FrameBuffer
import cv2

relay = MediaRelay()
logger = logging.getLogger("WHIPIngestServer")


@serve.deployment(route_prefix="/whip_ingest")
@serve.ingress(web.Application)
class WHIPIngestServer:
    def __init__(self, input_buffer, output_buffer):
        self.pcs = set()
        self.input_buffer = input_buffer
        self.output_buffer = output_buffer

    @web.post("/")
    async def ingest(self, request):
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

        @pc.on("track")
        def on_track(track):
            logger.info(f"Track {track.kind} received")
            if track.kind == "video":
                local_video = VideoFrameHandlerTrack(relay.subscribe(track), self.input_buffer, self.output_buffer)
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


class VideoFrameHandlerTrack:
    def __init__(self, track, input_buffer, output_buffer):
        self.track = track
        self.input_buffer = input_buffer
        self.output_buffer = output_buffer

    async def recv(self):
        try:
            frame = await self.track.recv()
            # Encode frame to bytes
            img = frame.to_ndarray(format="bgr24")
            _, buffer = cv2.imencode('.jpg', img)
            frame_bytes = buffer.tobytes()

            # If pipeline is available, add frame to input buffer
            pipeline_available = await self.input_buffer.pipeline_available.remote()
            if pipeline_available:
                await self.input_buffer.add_frame.remote(frame_bytes)
            else:
                # Pass-through: directly add to output buffer
                await self.output_buffer.add_frame.remote(frame_bytes)

            return frame
        except Exception as e:
            logger.exception(f"Error in VideoFrameHandlerTrack recv: {e}")
            # Return an empty frame or handle appropriately
            return None
