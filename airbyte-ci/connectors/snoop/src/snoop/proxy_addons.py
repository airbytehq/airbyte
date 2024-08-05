
import asyncio
import logging
import time
from snoop.publish import publish_to_topic

class HttpTrafficTelemetry:
    async def response(flow):
        logging.info(f"handle request: {flow.request.host}{flow.request.path}")
        await asyncio.sleep(5)
        logging.info(f"start  request: {flow.request.host}{flow.request.path}")

addons = [HttpTrafficTelemetry()]
