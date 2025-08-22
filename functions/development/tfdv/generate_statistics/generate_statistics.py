from typing import Any, Dict

import mlrun
import tensorflow_data_validation as tfdv
from mlrun.execution import MLClientCtx
from tensorflow_data_validation.utils.display_util import get_statistics_html


def generate_statistics(
        context: MLClientCtx,
        dataset_uri: str,
        schema_file: str,
        stats_options: Dict[str, Any]
) -> None:
    # load the dataset
    context.logger.info("Loading Dataset")
    df = mlrun.get_dataitem(dataset_uri).as_df()

    # update stats with schema_file
    if schema_file:
        stats_options["schema"] = tfdv.load_schema_text(schema_file)

    # compute statistics
    context.logger.info("Computing statistics")
    statistics = tfdv.generate_statistics_from_dataframe(
        dataframe=df,
        stats_options=tfdv.StatsOptions(**stats_options)
    )

    # output the results
    context.log_result(key="statistics", value=statistics)

    # visualize the statistics
    context.logger.info("Generating statistics HTML")
    context.log_artifact(item="statistics_html",
                         body=get_statistics_html(statistics),
                         format="html")