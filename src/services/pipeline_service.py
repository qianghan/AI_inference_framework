# src/services/pipeline_service.py

import logging
from aiohttp import web
from ray import serve

logger = logging.getLogger("PipelineService")


@serve.deployment(route_prefix="/pipeline")
@serve.ingress(web.Application)
class PipelineService:
    def __init__(self, engine_handle):
        self.engine = engine_handle

    @web.middleware
    async def handle_request(self, request, handler):
        try:
            response = await handler(request)
            return response
        except Exception as e:
            logger.exception(f"Error handling request: {e}")
            return web.Response(text="Internal server error.", status=500)

    @web.post("/")
    async def post_handler(self, request):
        try:
            return await self.engine.handle_request.remote(request)
        except Exception as e:
            logger.exception(f"Error in pipeline service: {e}")
            return web.Response(text="Internal server error.", status=500)
