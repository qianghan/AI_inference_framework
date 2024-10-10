# deployment/deploy.py

import ray
from ray import serve
from src.services.whip_ingest_server import WHIPIngestServer
from src.services.whep_playback_server import WHEPPlaybackServer
from src.services.pipeline_service import PipelineService
from src.services.rtmp_ingest_server import RTMPIngestServer
from src.core.engine import Engine
from src.core.utils import FrameBuffer
import logging

logger = logging.getLogger("Deployment")


def main(args):
    try:
        ray.init()
        serve.start()

        # Create frame buffers
        input_buffer = FrameBuffer.options(name="input_buffer").remote()
        output_buffer = FrameBuffer.options(name="output_buffer").remote()

        # Initialize the engine
        engine = Engine.options(name="engine").remote(config_path='configs/default_pipeline.yaml')

        # Set pipeline availability
        pipeline_available = args.deploy_pipeline
        input_buffer.set_pipeline_available.remote(pipeline_available)

        # Deploy services based on arguments
        deployments = []

        if args.deploy_whip:
            whip_ingest_server = WHIPIngestServer.bind(input_buffer, output_buffer)
            deployments.append(whip_ingest_server)

        if args.deploy_whep:
            whep_playback_server = WHEPPlaybackServer.bind(output_buffer)
            deployments.append(whep_playback_server)

        if args.deploy_rtmp:
            rtmp_ingest_server = RTMPIngestServer.bind(input_buffer, output_buffer)
            deployments.append(rtmp_ingest_server)

        if args.deploy_pipeline:
            pipeline_service = PipelineService.bind(engine)
            deployments.append(pipeline_service)

        if deployments:
            serve.run(deployments)
            logger.info("Services deployed successfully.")
        else:
            logger.error("No services specified for deployment.")
            print("Please specify at least one service to deploy.")
    except Exception as e:
        logger.exception(f"Error during deployment: {e}")
