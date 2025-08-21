from contextlib import closing
from typing import Optional, Union

import mlrun
import pandas as pd
import trino
from trino.auth import BasicAuthentication
from mlrun.execution import MLClientCtx


def query_to_dataset(
    context: MLClientCtx,
    query: str,
    schema: str,
    catalog: str,
    dataset_name: str,
    tag: Optional[str]=None) -> None:
    """Execute a SQL query and store the result in a dataset.

    :param context: function execution context
    :param query: SQL query to execute
    :param schema: database schema
    :param catalog: database catalog
    :param dataset_name: name of the dataset to create
    :param tag: optional tag for the dataset
    """
    # --- Secure connection params (secrets or env) ---
    host = mlrun.get_secret_or_env("TRINO_HOST")
    port = mlrun.get_secret_or_env("TRINO_PORT", default="8080")
    user = mlrun.get_secret_or_env("TRINO_USER", default="mlrun")
    verify = mlrun.get_secret_or_env("TRINO_TLS_VERIFY", default="true").lower() == "true"
        

    # Optional password-based auth (prefer secrets)
    password = mlrun.get_secret_or_env("TRINO_PASSWORD")
    auth = BasicAuthentication(user, password) if password else None
   
    # connect to trino 
    context.logger.info("Connecting to Trino")
    conn = trino.dbapi.connect(
        host=host,
        port=port,
        user=user,
        catalog=catalog,
        schema=schema,
        auth=auth,
        verify=verify
    )

    # execute the query
    context.logger.info("Executing SQL query")
    with closing(conn.cursor()) as cur:
        # TODO: consider implementing chunking
        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(rows, columns=columns)

    # log the dataset
    context.logger.info("Logging dataset")
    context.log_dataset(
        key=dataset_name,
        df=df,
        tag=tag,
    )

    # log the result
    context.log_result(key="rows", value=len(rows))
