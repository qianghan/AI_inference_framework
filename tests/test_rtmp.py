# tests/test_rtmp.py

import unittest
import requests
import time
import threading
import logging
import subprocess
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestRTMP")


class TestRTMP(unittest.TestCase):
    def test_rtmp_ingest(self):
        # Ensure an RTMP server is running at rtmp://localhost:1935/live/test
        # For testing purposes, we will simulate streaming to the RTMP ingest endpoint

        stream_url = "rtmp://localhost:1935/live/test"

        # Start the RTMP ingest by sending the stream URL to the server
        response = requests.post('http://localhost:8000/rtmp_ingest', json={"stream_url": stream_url})
        self.assertEqual(response.status_code, 200)

        # Start streaming a sample video to the RTMP server using FFmpeg
        ffmpeg_command = [
            'ffmpeg',
            '-re',
            '-stream_loop', '-1',
            '-i', 'tests/sample_video.mp4',
            '-c', 'copy',
            '-f', 'flv',
            stream_url
        ]

        # Run FFmpeg in a subprocess
        ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Let the streaming run for 10 seconds
        time.sleep(10)

        # Terminate FFmpeg process
        ffmpeg_process.terminate()
        ffmpeg_process.wait()

        # Check if the process exited cleanly
        self.assertEqual(ffmpeg_process.returncode, 0)

        # If no exceptions, the test passes
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
