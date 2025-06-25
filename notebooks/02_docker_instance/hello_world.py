
import mlrun

# get the logger
import logging
logger = logging.getLogger(__name__)

def handler(context: mlrun.MLClientCtx = None):
    logger.info("Hello world")

    context.log_result("hello", "world")

    return "Hello world result!"
