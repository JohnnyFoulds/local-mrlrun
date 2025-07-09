import joblib
import mlrun
import mlrun.feature_store as fstore
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


def train_model(context):
    data_uri = str(context.get_input("dataset"))
    print(data_uri)
    #df = mlrun.get_dataitem(url=data_uri).as_df()
    
    # X = df.drop("label", axis=1)
    # y = df["label"]

    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    # model = RandomForestClassifier()
    # model.fit(X_train, y_train)
    # acc = model.score(X_test, y_test)

    # context.log_result("accuracy", acc)
    # joblib.dump(model, "model.joblib")
    # context.log_model("rf-model", model_file="model.joblib")
