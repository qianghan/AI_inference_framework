# tests/test_whip.py

import asyncio
import unittest
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestWHIP")


class TestWHIP(unittest.IsolatedAsyncioTestCase):
    async def test_whip_ingest(self):
        pc = RTCPeerConnection()
        media = MediaPlayer('tests/sample_video.mp4')

        @pc.on('iceconnectionstatechange')
        async def on_iceconnectionstatechange():
            if pc.iceConnectionState == 'failed':
                await pc.close()

        # Add the media track to the peer connection
        pc.addTrack(media.video)

        # Create an offer and set it as the local description
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        # Send the offer to the server
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:8000/whip_ingest', json={
                'sdp': pc.localDescription.sdp,
                'type': pc.localDescription.type
            }) as resp:
                self.assertEqual(resp.status, 200)
                answer = await resp.json()

        # Set the remote description
        await pc.setRemoteDescription(
            RTCSessionDescription(sdp=answer['sdp'], type=answer['type'])
        )

        # Keep the connection alive for a short period
        await asyncio.sleep(5)

        await pc.close()
        self.assertTrue(True)  # If no exceptions, the test passes


if __name__ == '__main__':
    unittest.main()
