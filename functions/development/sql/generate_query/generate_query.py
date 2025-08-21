from typing import Any, Dict

from jinja2 import Template
from mlrun.execution import MLClientCtx


def generate_query(
    context: MLClientCtx,
    input_file: str,
    replacements: Dict[str, Any],
) -> None:
    """Read a template SQL file from a project artifact and replace placeholder using Jinja.

    :param context:    function execution context
    :param input_file: path to the SQL template file
    """
    # load the template
    context.logger.info("Loading SQL template from artifact")
    with open(input_file, "r") as f:
        query_template = f.read()

    # perform replacements
    context.logger.info("Performing replacements in the SQL template")

    context.log_result(
        key="sql",
        value=Template(query_template).render(**replacements)
    )
