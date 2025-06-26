import mlrun
from util import hi_there

# get the logger
import logging
logger = logging.getLogger(__name__)

def handler(context: mlrun.MLClientCtx = None):
    logger.info("Hello Complext world")

    context.log_result("world", "is_complex--" + hi_there())