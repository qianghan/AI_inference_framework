# src/main.py
# To start the application and deploy the WHIP and WHEP services along with the pipeline service, you can run:
# python src/main.py --deploy-whip --deploy-whep --deploy-pipeline


import argparse
import logging
from deployment.deploy import main as deploy_main

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Main")

if __name__ == "__main__":
    try:
        # Parse command-line arguments
        parser = argparse.ArgumentParser(description="Start the AI Inference Framework.")
        parser.add_argument('--deploy-whip', action='store_true', help='Deploy WHIP Ingest Server')
        parser.add_argument('--deploy-whep', action='store_true', help='Deploy WHEP Playback Server')
        parser.add_argument('--deploy-rtmp', action='store_true', help='Deploy RTMP Ingest Server')
        parser.add_argument('--deploy-pipeline', action='store_true', help='Deploy Pipeline Service')
        args = parser.parse_args()

        # Start deployment with provided arguments
        deploy_main(args)
    except Exception as e:
        logger.exception(f"Error in main application: {e}")

