# Docstring Examples from Existing Tools

This file contains examples of docstrings from various existing relevant tools and libraries (MLRun, ZenML, PEP8), showcasing different styles and conventions used in documenting code.

## Rationale

The aim of this document is to standardize the high-level structure of docstrings: what they should contain, and how to say it. Specific markup syntax will also be provided to ensure docstrings are consistent with downstream tools such as [MLRun](https://docs.mlrun.org/en/v1.9/) and [ZenML](https://docs.zenml.io/).

If you violate these conventions, or your Python code is not properly documented, your code may be rejected during the code review process.

## Basic Conventions

Please see [PEP 257](https://peps.python.org/pep-0257/) for the following details:

- [What is a Docstring?](https://peps.python.org/pep-0257/#what-is-a-docstring)
- [One-line Docstrings](https://peps.python.org/pep-0257/#one-line-docstrings)
- [Multi-line Docstrings](https://peps.python.org/pep-0257/#multi-line-docstrings)

Notes

- One-liners are for really obvious cases. They are not permissible for any function/method/class/module that takes parameters or has a return value.
- Documentation strings are **mandatory** for all public and all non-public modules, functions, classes, and methods.

## Docstring Format

For consistency, all Python docstrings in this codebase must use the **reStructuredText / Sphinx-style field-list format**, i.e. `:param name: …`, `:returns: …`, `:raises …:` etc., as illustrated in the references below.

- [Writing docstrings,” Sphinx-RTD Tutorial Documentation.](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html)
- [How to Write Docstrings in Python: reStructuredText](https://realpython.com/how-to-write-docstrings-in-python/#restructuredtext-docstrings)

Notes

- `:type name: …` is optional and may be omitted if the type can be inferred from type hints.
- For all **tool functions** (public entry points intended for external use), the docstring **must include an** `example::` block that demonstrates typical usage of the function. The example should be minimal but complete and must be valid Python code.

Example

```python
from typing import Annotated, Optional

import pandas as pd
from sklearn.datasets import load_iris


def training_data_loader(
    shuffle: bool = False,
    random_state: Optional[int] = None,
) -> Annotated[pd.DataFrame, "iris_dataset"]:
    """
    Load the iris dataset as a pandas dataframe for downstream steps.

    example::

        from my_project.data import training_data_loader

        df = training_data_loader(shuffle=True, random_state=42)
        print(df.head())

    :param shuffle:       Whether to shuffle the dataset rows before returning.
    :param random_state:  Optional random seed used when shuffling. Has no effect
                          if ``shuffle`` is ``False``.
    :returns:             A dataframe containing the iris features and target. The
                          dataset is also registered as the ``"iris_dataset"``
                          output via the :class:`typing.Annotated` return type.
    :raises ValueError:   If ``random_state`` is provided while ``shuffle`` is ``False``.
    """
    iris = load_iris(as_frame=True)

    if random_state is not None and not shuffle:
        raise ValueError("random_state has no effect when shuffle is False")

    frame = iris["frame"]
    if shuffle:
        frame = frame.sample(frac=1.0, random_state=random_state).reset_index(drop=True)

    return frame
```

## MLRun

The following examples is taken from [MLRun's Function Hub](https://github.com/mlrun/functions):

### Aggregate Function

```python
def aggregate(context,
              df_artifact: Union[DataItem, pd.core.frame.DataFrame],
              save_to: str = 'aggregated-df.pq',
              keys: list = None,
              metrics: list = None,
              labels: list = None,
              metric_aggregations: list = ['mean'],
              label_aggregations: list = ['max'],
              suffix: str = '',
              window: int = 3,
              center: bool = False,
              inplace: bool = False,
              drop_na: bool = True,
              files_to_select: int = 1):
    """Time-series aggregation function
    
    Will perform a rolling aggregation on {df_artifact}, over {window} by the selected {keys}
    applying {metric_aggregations} on {metrics} and {label_aggregations} on {labels}. adding {suffix} to the
    feature names.
    
    if not {inplace}, will return the original {df_artifact}, joined by the aggregated result.

    :param context: After running a job, you need to be able to track it. To gain the maximum value, MLRun uses the
                    job context object inside the code. This provides access to job metadata, parameters,
                    inputs, secrets, and API for logging and monitoring the results, as well as log text, files,
                    artifacts, and labels.
    
    :param df_artifact: MLRun input pointing to pandas dataframe (csv/parquet file path) or a 
                        directory containing parquet files.
                        * When given a directory the latest {files_to_select} will be selected
    :param save_to:     Where to save the result dataframe.
                        * If relative will add to the {artifact_path}
    :param keys:        Subset of indexes from the source dataframe to aggregate by (default=all)
    :param metrics:     Array containing a list of metrics to run the aggregations on. (default=None) 
    :param labels:      Array containing a list of labels to run the aggregations on. (default=None) 
    :param metric_aggregations: Array containing a list of aggregation function names to run on {metrics}.
                        (Ex: 'mean', 'std') (default='mean')
    :param label_aggregations:  Array containing a list of aggregation function names to run on {metrics}.
                        (Ex: 'max', 'min') (default='max') 
    :param suffix:      Suffix to add to the feature name, E.g: <Feature_Name>_<Agg_Function>_<Suffix>
                        (Ex: 'last_60_minutes') (default='')
    :param window:      Window size to perform the rolling aggregate on. (default=3)
    :param center:      If True, Sets the value for the central sample in the window,
                        If False, will set the value to the last sample. (default=False)
    :param inplace:     If True, will return only the aggregated results.
                        If False, will join the aggregated results with the original dataframe
    :param drop_na:     Will drop na lines due to the Rolling.
    :param files_to_select: Specifies the number of *latest* files to select (and concat) for aggregation.
    """
```

### Auto Trainer Function

```python
def train(
    context: MLClientCtx,
    dataset: DataItem,
    model_class: str,
    label_columns: Optional[Union[str, List[str]]] = None,
    drop_columns: List[str] = None,
    model_name: str = "model",
    tag: str = "",
    sample_set: DataItem = None,
    test_set: DataItem = None,
    train_test_split_size: float = None,
    random_state: int = None,
    labels: dict = None,
    **kwargs,
):
    """
    Training a model with the given dataset.

    example::

        import mlrun
        project = mlrun.get_or_create_project("my-project")
        project.set_function("hub://auto_trainer", "train")
        trainer_run = project.run(
            name="train",
            handler="train",
            inputs={"dataset": "./path/to/dataset.csv"},
            params={
                "model_class": "sklearn.linear_model.LogisticRegression",
                "label_columns": "label",
                "drop_columns": "id",
                "model_name": "my-model",
                "tag": "v1.0.0",
                "sample_set": "./path/to/sample_set.csv",
                "test_set": "./path/to/test_set.csv",
                "CLASS_solver": "liblinear",
            },
        )

    :param context:                 MLRun context
    :param dataset:                 The dataset to train the model on. Can be either a URI or a FeatureVector
    :param model_class:             The class of the model, e.g. `sklearn.linear_model.LogisticRegression`
    :param label_columns:           The target label(s) of the column(s) in the dataset. for Regression or
                                    Classification tasks. Mandatory when dataset is not a FeatureVector.
    :param drop_columns:            str or a list of strings that represent the columns to drop
    :param model_name:              The model's name to use for storing the model artifact, default to 'model'
    :param tag:                     The model's tag to log with
    :param sample_set:              A sample set of inputs for the model for logging its stats along the model in favour
                                    of model monitoring. Can be either a URI or a FeatureVector
    :param test_set:                The test set to train the model with.
    :param train_test_split_size:   if test_set was provided then this argument is ignored.
                                    Should be between 0.0 and 1.0 and represent the proportion of the dataset to include
                                    in the test split. The size of the Training set is set to the complement of this
                                    value. Default = 0.2
    :param random_state:            Relevant only when using train_test_split_size.
                                    A random state seed to shuffle the data. For more information, see:
                                    https://scikit-learn.org/stable/glossary.html#term-random_state
                                    Notice that here we only pass integer values.
    :param labels:                  Labels to log with the model
    :param kwargs:                  Here you can pass keyword arguments with prefixes,
                                    that will be parsed and passed to the relevant function, by the following prefixes:
                                    - `CLASS_` - for the model class arguments
                                    - `FIT_` - for the `fit` function arguments
                                    - `TRAIN_` - for the `train` function (in xgb or lgbm train function - future)

    """
```

### Batch Inference Function

```python
def _read_dataset_as_dataframe(
    dataset: DatasetType,
    feature_columns: Union[str, List[str]] = None,
    label_columns: Union[str, List[str]] = None,
    drop_columns: Union[str, List[str], int, List[int]] = None,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Parse the given dataset into a DataFrame and drop the columns accordingly. In addition, the label columns will be
    parsed and validated as well.

    :param dataset:         A dataset that will be converted into a DataFrame.
                            Can be either a list of lists, dict, URI or a FeatureVector.
    :param feature_columns: List of feature columns that will be used to build the dataframe when dataset is from
                            type list or numpy array.
    :param label_columns:   The target label(s) of the column(s) in the dataset. for Regression or
                            Classification tasks.
    :param drop_columns:    ``str`` / ``int`` or a list of ``str`` / ``int`` that represent the column names / indices
                            to drop.

    :returns: A tuple of:
              [0] = The parsed dataset as a DataFrame
              [1] = Label columns.

    raises MLRunInvalidArgumentError: If the `drop_columns` are not matching the dataset or unsupported dataset type.
    """
```

### Describe Function

```python
def analyze(
    context: MLClientCtx,
    name: str = "dataset",
    table: Union[FeatureSet, DataItem] = None,
    label_column: str = None,
    plots_dest: str = "plots",
    random_state: int = 1,
    problem_type: str = "classification",
    dask_key: str = "dask_key",
    dask_function: str = None,
    dask_client=None,
) -> None:
    """
    The function will output the following artifacts per
    column within the data frame (based on data types)
    If the data has more than 500,000 sample we
    sample randomly 500,000 samples:

    describe csv
    histograms
    scatter-2d
    violin chart
    correlation-matrix chart
    correlation-matrix csv
    imbalance pie chart
    imbalance-weights-vec csv

    :param context:                 The function context
    :param name:                    Key of dataset to database ("dataset" for default)
    :param table:                   MLRun input pointing to pandas dataframe (csv/parquet file path) or FeatureSet
                                    as param
    :param label_column:            Ground truth column label
    :param plots_dest:              Destination folder of summary plots (relative to artifact_path)
                                    ("plots" for default)
    :param random_state:            When the table has more than 500,000 samples, we sample randomly 500,000 samples
    :param problem_type             The type of the ML problem the data facing - regression, classification or None
                                    (classification for default)
    :param dask_key:                Key of dataframe in dask client "datasets" attribute
    :param dask_function:           Dask function url (db://..)
    :param dask_client:             Dask client object
    """
```

## ZenML

### Giving names to your artifacts

In ZenML assigning custom names to your artifacts can greatly enhance their discoverability and manageability. As best practice, utilize the `Annotated` object within your steps to give precise, human-readable names to outputs:

```python
from typing import Annotated
import pandas as pd
from sklearn.datasets import load_iris

from zenml import pipeline, step

# Using Annotated to name our dataset
@step
def training_data_loader() -> Annotated[pd.DataFrame, "iris_dataset"]:
    """Load the iris dataset as pandas dataframe."""
    iris = load_iris(as_frame=True)
    return iris.get("frame")


@pipeline
def feature_engineering_pipeline():
    training_data_loader()


if __name__ == "__main__":
    feature_engineering_pipeline()
```

### Other Examples

source:  
https://github.com/zenml-io/zenml/blob/main/examples/agent_outer_loop/steps/data.py

```python
def load_toy_intent_data() -> Tuple[
    Annotated[List[str], "texts"], Annotated[List[str], "labels"]
]:
    """Load small toy dataset for intent classification.

    Returns:
        Tuple of (texts, labels) for training the intent classifier.
    """
```

source:
https://github.com/zenml-io/zenml-projects/blob/main/retail-forecast/steps/model_trainer.py

```python
def train_model(
    train_data_dict: Dict[str, pd.DataFrame],
    series_ids: List[str],
    weekly_seasonality: bool = True,
    yearly_seasonality: bool = False,
    daily_seasonality: bool = False,
    seasonality_mode: str = "multiplicative",
) -> Annotated[Dict[str, Prophet], "trained_prophet_models"]:
    """Train a Prophet model for each store-item combination.

    Args:
        train_data_dict: Dictionary with training data for each series
        series_ids: List of series identifiers
        weekly_seasonality: Whether to include weekly seasonality
        yearly_seasonality: Whether to include yearly seasonality
        daily_seasonality: Whether to include daily seasonality
        seasonality_mode: 'additive' or 'multiplicative'

    Returns:
        Dictionary of trained Prophet models for each series
    """
```

## References

- [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/)
- [MLRun Function Hub Repository](https://github.com/mlrun/functions)
- [Napoleon - Marching toward legible docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/#id1)
- [PEP 287 – reStructuredText Docstring Format](https://peps.python.org/pep-0287/)
- [How to Write Docstrings in Python](https://realpython.com/how-to-write-docstrings-in-python/)
- [Documenting Python Code: A Complete Guide](https://realpython.com/documenting-python-code/)
