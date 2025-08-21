# Deploying Apache Spark for MLRun

This document details how to deploy Apache Spark on your K3s cluster and configure it to work seamlessly with your existing MLRun, MinIO, and Iceberg/Polaris stack.

The strategy is to use the **Spark on Kubernetes Operator**, which allows you to define and manage Spark applications as native Kubernetes resources. MLRun has built-in support for this operator, making it the perfect choice for orchestrating complex PySpark jobs.

## Architecture Overview

1.  **Spark Operator:** A Kubernetes controller that watches for `SparkApplication` custom resources and manages the lifecycle of Spark jobs (creating driver and executor pods).
2.  **Custom Spark Image:** A custom Docker image containing PySpark and all necessary JARs (for Iceberg, S3, Kafka) will be built and pushed to your local registry. This is best practice for dependency management.
3.  **Service Account & RBAC:** A dedicated Kubernetes `ServiceAccount` will be created with the necessary permissions for Spark jobs to create and manage their own executor pods.
4.  **MLRun Integration:** MLRun will be configured to use the Spark Operator. When you run a function with `kind="spark"`, MLRun will automatically generate the `SparkApplication` manifest and apply it to the cluster.

---

## Prerequisites

1.  Your K3s cluster is running (`01_k3s.md`).
2.  Helm v3 is installed (`01_k3s.md`).
3.  Your local Docker registry is running and accessible (`03_local_registry.md`).
4.  MinIO and Polaris are deployed in the `data` namespace (`01_trino.md`).
5.  MLRun is deployed in the `mlrun` namespace (`04_mlrun.md`).
6.  You have GPU nodes with the NVIDIA container runtime configured (`02_nvidia_container.md`).

---

## Step 1: Install the Spark on Kubernetes Operator

First, we'll deploy the operator itself, which will manage our Spark jobs.

```bash
# Create a dedicated namespace for the operator
sudo kubectl create namespace spark-operator

# Add the Spark Operator Helm repository
helm repo add spark-operator https://googlecloudplatform.github.io/spark-on-k8s-operator
helm repo update

# Install the Spark Operator into its namespace
helm install spark-operator spark-operator/spark-operator \
    --namespace spark-operator \
    --set sparkJobNamespace=data,mlrun \
    --set webhook.enable=true
```
*   `sparkJobNamespace=data,mlrun`: This is crucial. It tells the operator to watch for `SparkApplication` resources in both your `data` and `mlrun` namespaces, allowing your jobs to be organized logically.
*   `webhook.enable=true`: Enables advanced features like resource mutation, which is good practice.

**Verify the installation:**
```bash
sudo kubectl get pods -n spark-operator
# You should see one or two spark-operator pods in a Running state.
```

---

## Step 2: Create RBAC for Spark Jobs

Spark jobs need permissions to create and manage their own executor pods. We will create a `ServiceAccount` in the `data` namespace for this purpose.

```bash
# Create a Service Account for Spark jobs in the 'data' namespace
sudo kubectl create serviceaccount spark -n data

# Create a Role that grants permissions to manage pods, services, and configmaps
cat <<EOF | sudo kubectl apply -n data -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: spark-job-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch", "create", "delete", "patch", "update"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: spark-job-role-binding
subjects:
- kind: ServiceAccount
  name: spark
  namespace: data
roleRef:
  kind: Role
  name: spark-job-role
  apiGroup: rbac.authorization.k8s.io
EOF```
Now, any Spark job we run using the `spark` service account in the `data` namespace will have the required permissions.

---

## Step 3: Build a Custom Spark Docker Image

To ensure Spark has all the drivers it needs to talk to MinIO (S3), Polaris (Iceberg), and Kafka, we'll build a custom image.

Create a new directory for your Spark image, for example `spark-image`, and create a `Dockerfile` inside it.

**`spark-image/Dockerfile`:**
```Dockerfile
# Use an official Spark image as the base.
# Choose a version compatible with the Iceberg libraries.
FROM apache/spark-py:v3.5.1

USER root

# Define versions for connectors
ENV ICEBERG_VERSION=1.5.0
ENV AWS_SDK_VERSION=2.26.12
ENV KAFKA_VERSION=3.7.1
ENV SCALA_VERSION=2.12

# Install necessary JARs for Iceberg, S3, Kafka, and OAuth2
RUN apt-get update && apt-get install -y wget && \
    JARS_DIR=/opt/spark/jars && \
    # Iceberg Runtime
    wget -P ${JARS_DIR} https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/${ICEBERG_VERSION}/iceberg-spark-runtime-3.5_2.12-${ICEBERG_VERSION}.jar && \
    # AWS S3 Bundle (includes dependencies)
    wget -P ${JARS_DIR} https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/${AWS_SDK_VERSION}/bundle-${AWS_SDK_VERSION}.jar && \
    # Kafka Client
    wget -P ${JARS_DIR} https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_${SCALA_VERSION}/3.5.1/spark-sql-kafka-0-10_${SCALA_VERSION}-3.5.1.jar && \
    # For Polaris REST Catalog OAuth2
    wget -P ${JARS_DIR} https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-rest-client/${ICEBERG_VERSION}/iceberg-rest-client-${ICEBERG_VERSION}.jar && \
    apt-get purge -y wget && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# (Optional) Pre-install Python libraries your jobs will need
# RUN pip install pandas scikit-learn

# Switch back to the Spark user
USER spark
```

Now, build and push this image to your local registry:

```bash
# Navigate to your Spark image directory
cd spark-image

# Build the image
docker build -t spark-mlrun:latest .

# Tag it for your local registry
docker tag spark-mlrun:latest dragon:30500/mlrun/spark-mlrun:latest

# Log in to your registry (if you haven't recently)
docker login -u mlrun dragon:30500  # Use mlrun/mlpass

# Push the image
docker push dragon:30500/mlrun/spark-mlrun:latest

# Verify the push
curl http://dragon:30500/v2/mlrun/spark-mlrun/tags/list -u mlrun:mlpass
```

---

## Step 4: Test with a Sample `SparkApplication`

Let's test the entire setup by submitting a `SparkApplication` manifest directly. This verifies the operator, RBAC, and custom image are all working before we integrate with MLRun.

Create a file named `spark-pi-test.yaml`:

**`spark-pi-test.yaml`:**
```yaml
apiVersion: "sparkoperator.k8s.io/v1beta2"
kind: SparkApplication
metadata:
  name: pyspark-pi
  namespace: data
spec:
  type: Python
  pythonVersion: "3"
  mode: cluster
  image: "dragon:30500/mlrun/spark-mlrun:latest"
  imagePullPolicy: Always
  mainApplicationFile: local:///opt/spark/examples/src/main/python/pi.py
  sparkVersion: "3.5.1"
  restartPolicy:
    type: Never
  driver:
    cores: 1
    coreLimit: "1200m"
    memory: "512m"
    labels:
      version: 3.5.1
    serviceAccount: spark # Use the ServiceAccount we created
  executor:
    cores: 1
    instances: 1
    memory: "512m"
    labels:
      version: 3.5.1
```

Apply it and watch the pods get created:

```bash
sudo kubectl apply -f spark-pi-test.yaml

# Watch the pods being created in the 'data' namespace
sudo kubectl get pods -n data -w
# You should see 'pyspark-pi-driver' and 'pyspark-pi-executor-...' pods appear

# Check the logs of the driver pod to see the result
sudo kubectl logs -n data pyspark-pi-driver
# You should see a line like "Pi is roughly 3.14..."
```

Once the job is complete, the pods will terminate. You can then delete the application resource:
```bash
sudo kubectl delete -f spark-pi-test.yaml
```

---

## Step 5: Integrate with MLRun

Now for the final step: running a Spark job through an MLRun function. This requires configuring the MLRun project to use our custom Spark setup.

### Summary of Your New Workflow with MLRun
1.  You will write your complex PySpark logic in a Python script.
2.  You will create an MLRun function of `kind="spark"`.
3.  In this function, you will specify your custom Docker image (`dragon:30500/mlrun/spark-mlrun:latest`).
4.  You will provide the PySpark script as the `command`.
5.  You will set Spark configurations (for MinIO, Polaris, etc.) in the function's `set_spark_conf()` method.
6.  When you run the function, MLRun generates the `SparkApplication` manifest and applies it to the cluster for you.

### Example MLRun Project Script

Here is an example of a Python script you would use to define and run a Spark job that reads/writes to your Iceberg table.

**`project_spark_ingest.py`**
```python
import mlrun
import os

# Load environment variables for credentials
from dotenv import load_dotenv
load_dotenv(".env")

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
POLARIS_URI = "http://polaris.data.svc.cluster.local:8181/api/catalog/"

def create_and_run_spark_ingest():
    """
    Defines and runs an MLRun Spark function to process data.
    """
    # Get or create an MLRun project
    project = mlrun.get_or_create_project("spark-demo", context="./")
    
    # Define the MLRun function for our Spark job
    spark_function = project.set_function(
        name="spark-ingest-job",
        kind="spark",
        image="dragon:30500/mlrun/spark-mlrun:latest",
        command="spark_ingest_logic.py" # The python file with the Spark code
    )
    
    # Configure the Spark Operator resources and settings
    spark_function.with_driver_requests(cpu="1", mem="512m")
    spark_function.with_executor_requests(cpu="1", mem="512m", replicas=2)
    
    # --- CRITICAL CONFIGURATION FOR YOUR STACK ---
    # Point Spark to the Polaris REST Catalog for Iceberg
    spark_function.set_spark_conf("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
    spark_function.set_spark_conf("spark.sql.catalog.iceberg.catalog-impl", "org.apache.iceberg.rest.RESTCatalog")
    spark_function.set_spark_conf("spark.sql.catalog.iceberg.uri", POLARIS_URI)
    spark_function.set_spark_conf("spark.sql.catalog.iceberg.warehouse", "main")
    spark_function.set_spark_conf("spark.sql.catalog.iceberg.credential", "root:secret") # For OAuth2
    spark_function.set_spark_conf("spark.sql.catalog.iceberg.oauth2.token-type", "bearer")
    
    # Configure S3a connection to your MinIO
    spark_function.set_spark_conf("spark.hadoop.fs.s3a.endpoint", S3_ENDPOINT_URL)
    spark_function.set_spark_conf("spark.hadoop.fs.s3a.access.key", AWS_ACCESS_KEY_ID)
    spark_function.set_spark_conf("spark.hadoop.fs.s3a.secret.key", AWS_SECRET_ACCESS_KEY)
    spark_function.set_spark_conf("spark.hadoop.fs.s3a.path.style.access", "true")
    spark_function.set_spark_conf("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

    # (Optional) Request a GPU for the driver
    spark_function.with_driver_node_selection(node_selector={"nvidia.com/gpu": "true"})
    spark_function.with_driver_requests(gpus=1)

    # Run the job
    print("Submitting Spark job through MLRun...")
    run_context = project.run_function(
        "spark-ingest-job",
        handler="main", # Assumes a main() function in your script
        returns=["row_count"]
    )
    print(f"Job submitted. Run context: {run_context.uid}")

if __name__ == "__main__":
    create_and_run_spark_ingest()

```

You would also need the actual PySpark code in `spark_ingest_logic.py`:

**`spark_ingest_logic.py`**
```python
from pyspark.sql import SparkSession
import mlrun

def main(context: mlrun.MLClientCtx):
    """
    Example PySpark job that reads and writes to Iceberg.
    """
    spark = SparkSession.builder.appName("MLRun-Iceberg-Ingest").getOrCreate()
    
    # Example: Create a dataframe
    data = [("Rey", "Skywalker"), ("Tony", "Stark")]
    columns = ["first_name", "last_name"]
    df = spark.createDataFrame(data, columns)
    
    # Write to your Iceberg table
    # This assumes the table 'iceberg.lakehouse.new_users' exists.
    # You would replace this with your Kafka reading and complex transformations.
    df.writeTo("iceberg.lakehouse.taxi_trips").append()

    print("Successfully appended data to the Iceberg table.")
    
    # Read the data back to verify
    print("Reading all data from the table:")
    result_df = spark.table("iceberg.lakehouse.taxi_trips")
    result_df.show()
    
    row_count = result_df.count()
    context.log_result("row_count", row_count)

    spark.stop()

```

With these files in place, you can simply run `python project_spark_ingest.py` from your terminal. MLRun will package the job, submit it to the Spark Operator, and track its execution, seamlessly integrating all components of your stack.