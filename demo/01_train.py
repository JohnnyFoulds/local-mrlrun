import joblib
import mlrun
import mlrun.feature_store as fstore
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


def train_model(context):
    # Load the dataset from the provided feature vector
    feature_vector_name = context.inputs.get("feature", None)
    context.logger.info(f"Loading dataset from feature vector: {feature_vector_name}")
    feature_vector = fstore.get_feature_vector(feature_vector_name)
    if not feature_vector:
        raise ValueError("Dataset not found or is empty.")

    df = feature_vector.get_offline_features().to_dataframe()

    context.logger.info("Starting training process...")
    print(df.head())
    
    # X = df.drop("label", axis=1)
    # y = df["label"]

    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    # model = RandomForestClassifier()
    # model.fit(X_train, y_train)
    # acc = model.score(X_test, y_test)

    # context.log_result("accuracy", acc)
    # joblib.dump(model, "model.joblib")
    # context.log_model("rf-model", model_file="model.joblib")
