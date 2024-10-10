# tests/test_whep.py

import asyncio
import unittest
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestWHEP")


class TestWHEP(unittest.IsolatedAsyncioTestCase):
    async def test_whep_playback(self):
        pc = RTCPeerConnection()
        media_blackhole = MediaBlackhole()

        @pc.on('track')
        def on_track(track):
            logger.info(f'Received track: {track.kind}')
            media_blackhole.addTrack(track)

        @pc.on('iceconnectionstatechange')
        async def on_iceconnectionstatechange():
            if pc.iceConnectionState == 'failed':
                await pc.close()

        # Create an offer and set it as the local description
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        # Send the offer to the server
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:8000/whep_playback', json={
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
        media_blackhole.stop()
        self.assertTrue(True)  # If no exceptions, the test passes


if __name__ == '__main__':
    unittest.main()
