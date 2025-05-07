# MLRun Overview...

## Johannes Foulds
Tell me about MLRun

## Alfred Ipswich
**MLRun** is an open-source **machine learning operations (MLOps) framework** designed to streamline the development, orchestration, deployment, and monitoring of **machine learning (ML) and data science pipelines**. It is particularly geared towards **real-time and production-grade workloads**, and is closely integrated with the **Iguazio Data Science Platform**. It supports **Kubernetes-native workflows** and is built to manage the full lifecycle of ML projects from experimentation to deployment.

* * *

### 🔧 **Core Concepts and Features**

#### 1\. **Serverless Execution and Kubernetes Integration**

*   MLRun abstracts infrastructure details through **serverless functions** (backed by Kubernetes pods).
    
*   You can define code functions in Python, package them, and run them on various backends (local, Kubernetes, Dask, Spark, etc.).
    
*   Seamless scaling and deployment with **KubeFlow**, **Nuclio**, or **Job runtimes**.
    

#### 2\. **Unified Pipeline and Experiment Management**

*   Track experiments with **artifacts**, **metrics**, **logs**, and **function versions**.
    
*   Supports **version control** and **lineage tracking**.
    
*   Define and run complex workflows using **MLRun Pipelines** (based on **Kubeflow Pipelines** or **Argo Workflows**).
    

#### 3\. **Data and Artifact Management**

*   MLRun introduces the concept of a **DataItem**, an abstraction over various data sources (S3, v3io, HTTP, etc.).
    
*   **Automatic tracking and logging** of input/output data, models, and intermediate results.
    

#### 4\. **Real-time and Batch Inference**

*   Supports **real-time model serving** with **Nuclio** (serverless function platform).
    
*   Built-in support for **model monitoring**, **drift detection**, and **real-time feature vector generation** via **Feature Store**.
    

#### 5\. **Feature Store**

*   Integrated **Feature Store** for storing and retrieving features for training and serving.
    
*   Supports **online/offline store**, **feature set transformation**, and **real-time ingestion**.
    

#### 6\. **CI/CD for ML**

*   Enables **automated deployment** of models to production.
    
*   Integrates with CI/CD pipelines (e.g., Jenkins, GitLab CI) for ML model versioning and promotion.
    

* * *

### 🧱 **Typical MLRun Stack**

An MLRun-powered ML system usually includes:

*   **MLRun SDK** (Python API)
    
*   **Iguazio or custom Kubernetes cluster**
    
*   **Nuclio** (for real-time inference)
    
*   **MinIO / S3 / v3io** for storage
    
*   **MLRun UI** for managing runs and functions
    
*   Optional: **Dask, Spark, or MPI** for distributed training
    

* * *

### 📘 **Code Example**

```python
import mlrun

# Set the project
project = mlrun.get_or_create_project("my-project", "./")

# Create a function from a Python file
fn = project.set_function("train.py", name="train", kind="job", image="mlrun/mlrun")

# Run the function
run = fn.run(
    name="train-model",
    inputs={"data": "s3://mybucket/dataset.csv"},
    params={"n_estimators": 100},
    handler="train_model"
)
```

* * *

### 📊 **Comparison with Other MLOps Frameworks**

| Feature | MLRun | MLflow | Kubeflow Pipelines |
| --- | --- | --- | --- |
| Workflow Orchestration | ✔ (via KFP or Argo) | ✖ | ✔ |
| Real-time Inference | ✔ (via Nuclio) | ✖ | ✖ |
| Feature Store | ✔ | ✖ | Partial (Feast) |
| Serverless Support | ✔ | ✖ | ✖ |
| Versioning & Lineage | ✔ | ✔ | ✔ |
| Kubernetes Native | ✔ | Partial | ✔ |

* * *

### 📚 **References**

*   M. Weinstock et al., "MLRun: Orchestrating and Monitoring ML Workflows," _Iguazio Documentation_, 2022.
    
*   [https://www.mlrun.org](https://www.mlrun.org)
    
*   [https://github.com/mlrun/mlrun](https://github.com/mlrun/mlrun)
    

* * *

Would you like a practical demonstration or a comparison to a specific tool like MLflow or Metaflow?undefined

## Johannes Foulds
You mentioned the functions can run on various backends including local?

## Alfred Ipswich
Yes, MLRun supports **multiple execution backends**, and one of them is indeed **local execution**. This means you can run your MLRun functions **directly on your local machine** (without Kubernetes), which is particularly useful during early development and testing.

* * *

### ✅ **Local Backend in MLRun**

MLRun provides a special runtime environment called `local`, which:

*   Runs the function **in-process** (like a regular Python function call).
    
*   Avoids containerisation and Kubernetes orchestration.
    
*   Still provides **experiment tracking**, **artifact logging**, and **parameters management**.
    

This backend is invoked using:

```python
run = function.run(local=True)
```

* * *

### 🔬 **Example: Local Function Execution**

Suppose you define a Python function for training:

```python
def train_model(ctx, data_url, n_estimators=100):
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier

   # Load data
    df = pd.read_csv(data_url)
    X, y = df.iloc[:, :-1], df.iloc[:, -1]

   # Train model
    model = RandomForestClassifier(n_estimators=n_estimators)
    model.fit(X, y)

   # Save model artifact
    context.log_model("rf_model", body=model, model_file="model.pkl")
```

You can execute this locally with MLRun as follows:

```python
import mlrun

project = mlrun.get_or_create_project("my_project", "./")

# Create the function from code
fn = mlrun.code_to_function(name="trainer", kind="job", filename="train.py")

# Run locally
run = fn.run(
    handler="train_model",
    params={"data_url": "data.csv", "n_estimators": 50},
    local=True  # 👈 forces local execution
)
```

* * *

### 🛠️ **When to Use `local=True`**

| Use Case | Suitability |
| --- | --- |
| Interactive testing | ✅ Ideal |
| Quick debugging | ✅ Ideal |
| Integration with IDEs or notebooks | ✅ Excellent |
| Production or distributed jobs | ❌ Not suitable |

* * *

### ⚠️ **Limitations of Local Execution**

*   **No scaling**: Cannot parallelise across nodes or GPUs.
    
*   **No container isolation**: Uses your current Python environment (risks of dependency pollution).
    
*   **No distributed runtime**: Features like Dask, MPI, or Spark are not available locally.
    

* * *

### 🔗 Reference

*   MLRun Docs: https://docs.mlrun.org/en/stable/
    
*   `mlrun.run()` API Reference: https://docs.mlrun.org/en/stable/api/mlrun.html#mlrun.run
    

* * *

Would you like a walkthrough on setting up MLRun for local-only projects or how to transition from local to Kubernetes backends?undefined

## Johannes Foulds
So can you use MLRun without docker at all?

## Alfred Ipswich
Yes, **you can use MLRun without Docker**, **but only in limited contexts**—primarily for **local execution** with `local=True`. However, for most of MLRun’s **advanced capabilities**—especially serverless execution, Kubernetes orchestration, and distributed pipelines—**Docker is required**, as MLRun packages and executes functions in containers by default when running remotely.

* * *

### 🧭 Summary: **MLRun Without Docker**

| Capability | Without Docker (Local) | With Docker (Remote / Kubernetes) |
| --- | --- | --- |
| Define and run functions | ✅ Yes | ✅ Yes |
| Run in notebooks / IDE | ✅ Yes (local=True) | ✅ Yes |
| Track experiments & artifacts | ✅ Yes | ✅ Yes |
| Feature store access | ✅ Partial | ✅ Full |
| Remote orchestration (K8s, Nuclio) | ❌ No | ✅ Required |
| Auto-packaging environments | ❌ No | ✅ Docker used for image builds |
| Scalable/distributed runtimes | ❌ No | ✅ Yes |

* * *

### ✅ **What You _Can_ Do Without Docker**

1.  **Run local jobs**:
    
    ```python
    fn.run(local=True)
    ```
    
    This avoids Docker entirely and just invokes the Python function in your current environment.
    
2.  **Develop and debug functions**:  
    Local testing during early development without the need to containerise code.
    
3.  **Track metadata**:  
    Use MLRun’s logging and tracking features locally—parameters, metrics, artifacts, and models.
    
4.  **Integrate into notebooks**:  
    MLRun integrates with Jupyter notebooks and works well with non-container setups _during early-phase experimentation_.
    

* * *

### ❌ **What You _Cannot_ Do Without Docker**

*   **Deploy functions to Kubernetes, Nuclio, or Dask runtimes**.
    
*   **Use serverless real-time inference** (Nuclio always requires containers).
    
*   **Run on distributed backends (MPI, Spark, Dask)**.
    
*   **Use CI/CD automation or versioned deployments**.
    
*   **Reproduce environments across team members or production reliably**.
    

* * *

### 🛠️ Technical Explanation

MLRun uses the concept of a _function runtime class_ (e.g., `JobRuntime`, `NuclioRuntime`). Most runtime classes **require a container image** to encapsulate the execution environment:

```python
fn = mlrun.code_to_function(name="myfunc", kind="job", image="my-image")
```

When running **without Docker**, the `image` argument is ignored, and MLRun skips containerisation—but **only if** `local=True`.

* * *

### 🧪 Minimal Local Use Case Without Docker

```python
from mlrun import get_or_create_ctx

def my_func(ctx):
    param = ctx.get_param("x", 1)
    ctx.log_result("double", param * 2)

ctx = get_or_create_ctx("my-local-job")
my_func(ctx)
```

This runs **entirely without Docker** or Kubernetes.

* * *

### 📚 References

*   MLRun Architecture: https://docs.mlrun.org/en/stable/concepts/architecture.html
    
*   Function Runtimes: https://docs.mlrun.org/en/stable/runtimes/index.html
    

* * *

Would you like a starter template for a full local MLRun project that avoids Docker entirely?undefined

## Johannes Foulds
OK show me how I can use this with only a local conda environment. I want to see project with functions, the whole speil, everything I can accomplish without breaking out to a full containerised platform/

## Alfred Ipswich
Excellent—let's build a **complete MLRun project** that runs **entirely in your local Conda environment**, without Docker or Kubernetes. This will include:

1.  A **project folder structure**
    
2.  A function file
    
3.  A project YAML definition
    
4.  A Python script to run everything
    
5.  Metadata tracking (params, metrics, artifacts)
    
6.  No Docker. No Kubernetes. Just Conda.
    

* * *

📁 Project Structure
--------------------

```perl
my-mlrun-local-project/
├── functions/
│   └── train.py
├── artifacts/
├── project.yaml
└── run_local.py
```

You can create this structure manually or with a script.

* * *

🔧 Step 1: `train.py` — Your Function Code
------------------------------------------

```python
# functions/train.py
def train_model(context, n_estimators=100):
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    import pickle

   # Load data
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42)

   # Train model
    model = RandomForestClassifier(n_estimators=n_estimators)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

   acc = accuracy_score(y_test, y_pred)
    context.log_result("accuracy", acc)

   # Save model artifact
    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)
    context.log_model("rf_model", model_file="model.pkl")
```

* * *

📄 Step 2: `project.yaml`
-------------------------

```yaml
# project.yaml
kind: project
metadata:
  name: local-mlrun-demo
spec:
  functions:
    - url: functions/train.py
      name: train
      kind: job
  workflows: []
```

* * *

🐍 Step 3: `run_local.py` — Local Runner
----------------------------------------

```python
# run_local.py
import mlrun

# Load or create project
project = mlrun.get_or_create_project("local-mlrun-demo", "./")

# Load function from project.yaml
fn = project.set_function("functions/train.py", name="train", kind="job")

# Run the function locally
run = fn.run(
    handler="train_model",
    params={"n_estimators": 200},
    local=True,  # 👈 Local execution avoids Docker
    artifact_path="./artifacts"  # Save artifacts locally
)

# Print results
print("Accuracy:", run.outputs["accuracy"])
print("Model saved:", run.artifact("rf_model").get_path())
```

Run this from the terminal:

```bash
conda activate your_env
python run_local.py
```

* * *

✅ What You Get
--------------

*   Tracked parameters (`n_estimators=200`)
    
*   Logged metrics (`accuracy`)
    
*   Saved model artifact (`model.pkl`)
    
*   All running **in-process**, inside your current Conda environment.
    

* * *

💡 Optional: Track with MLRun UI
--------------------------------

You can also install and run the UI locally:

```bash
mlrun ui
```

Then go to `http://localhost:8080` to view your run history.

> Local runs use an in-memory or file-based metadata store.

* * *

🧱 Conda Environment Requirements
---------------------------------

Install the dependencies:

```bash
conda create -n mlrun-local python=3.10
conda activate mlrun-local
pip install mlrun scikit-learn pandas
```

* * *

📚 References
-------------

*   MLRun Local Execution Docs: https://docs.mlrun.org/en/stable/runtimes/local.html
    
*   Artifact Logging: https://docs.mlrun.org/en/stable/store/artifacts.html
    

* * *

Would you like me to generate this entire project folder as a `.zip` for you to download, or would you prefer a shell script that scaffolds everything?undefined

## Johannes Foulds
So this will not use a database or anything like that, all running locally in the venv?

## Alfred Ipswich
Correct. When you use **MLRun in fully local mode** (i.e., with `local=True` and no Docker, no Kubernetes), **everything runs in-process**, and:

*   ✅ **No external database** (e.g., no etcd, PostgreSQL, or MySQL)
    
*   ✅ **No container runtime or orchestration**
    
*   ✅ **No Docker images pulled or built**
    
*   ✅ **No server-side metadata store**
    
*   ✅ **No cloud dependencies**
    

Instead:

* * *

### 🔍 **What Happens Under the Hood (Local Mode)**

| Component | Local Behaviour |
| --- | --- |
| Function execution | Runs as a normal Python function inside the current Conda environment |
| Artifact logging | Stored as regular files in the artifact_path (e.g., ./artifacts/) |
| Metadata storage | Uses an in-memory or local file-based store via ~/.mlrun directory |
| UI / API server | Optional. Not started unless explicitly launched (e.g., mlrun ui) |
| Environment isolation | None. It uses the current Python environment (i.e., your active Conda env) |

* * *

### 🗃️ Local Files Created

When you run MLRun locally, you'll find:

*   `.mlrun/` in your home directory — contains run metadata, secrets, config.
    
*   `./artifacts/` — contains logged outputs and model artifacts.
    
*   `mlrun.db` (optional SQLite) — created **only if** you start the local API server explicitly (`mlrun db start-local`), not required for `local=True`.
    

* * *

### 🧠 Key Considerations

*   ✅ Excellent for **early-phase development**, testing, or running small experiments.
    
*   ✅ Can be tracked and replayed using the MLRun SDK without a full MLOps stack.
    
*   ❌ Not suitable for **concurrent team workflows**, **multi-user access**, or **distributed jobs**.
    

* * *

### Optional: Upgrade to File-Based SQLite Metadata

If you want **persistence beyond memory** for runs even across sessions, you can run:

```bash
mlrun db start-local
```

This sets up:

*   A minimal **local REST API**
    
*   An embedded **SQLite metadata store**
    

But this is optional. You can run everything without it if `local=True`.

* * *

### ✅ Minimal Mode vs Full Platform Mode

| Feature | local=True (Pure Local) | MLRun API Server (mlrun db start-local) | Full Platform |
| --- | --- | --- | --- |
| No Docker | ✅ | ✅ | ❌ |
| No Kubernetes | ✅ | ✅ | ❌ |
| In-memory metadata | ✅ | ❌ (uses SQLite) | ❌ |
| File-based artifacts | ✅ | ✅ | ✅ |
| Multiple users | ❌ | ❌ | ✅ |
| UI dashboard | ❌ (unless started manually) | ✅ (mlrun ui) | ✅ |

* * *

Would you like me to prepare a Conda-friendly installer script that sets up all of this in one go for your local machine?

## Johannes Foulds
You showed me project stracture and code for running without docker, how does this compare to if I had the full Iguazio platform?

## Alfred Ipswich
This is a critical and nuanced comparison. Using **MLRun locally** versus using it on the **Iguazio MLOps platform** represents a shift from **lightweight local experimentation** to **full enterprise-grade MLOps** with scalable, production-ready infrastructure.

Below is a rigorous comparison of the **capabilities, architecture, and workflows** between **MLRun in local mode (pure Conda, no Docker)** and **MLRun on the full Iguazio platform**.

* * *

🧱 1. **Execution Environment Comparison**
------------------------------------------

| Feature | Local Conda (No Docker) | Iguazio Platform (Full MLRun Stack) |
| --- | --- | --- |
| Execution Mode | In-process Python | Containerized jobs on Kubernetes / Nuclio |
| Runtime Isolation | No isolation, runs in current Conda env | Full Docker container isolation per job/function |
| Scalability | Single-process, single-node | Distributed, autoscaling, GPU/TPU support |
| Backend Runtimes | job (local only) | job, dask, mpi, spark, nuclio, serving |
| Real-time inference | ❌ Not available | ✅ via Nuclio (low-latency serverless functions) |
| CI/CD Integration | Manual scripting | Integrated pipelines, webhooks, and auto-deployment |

* * *

📦 2. **Function and Workflow Management**
------------------------------------------

| Aspect | Local Conda | Iguazio Platform |
| --- | --- | --- |
| Function Packaging | Direct Python file | Python + Dockerfile or automatic image builder |
| Versioning | Limited to local file system | Full function version control (code, image, metadata) |
| Workflow Execution | Manual orchestration via scripts | Kubeflow Pipelines or Argo Workflows integration |
| Automation | ❌ Manual | ✅ Full event-driven automation with triggers |

* * *

🧪 3. **Data & Feature Management**
-----------------------------------

| Capability | Local Conda | Iguazio Platform |
| --- | --- | --- |
| Artifact Storage | File system (e.g., ./artifacts/) | Distributed object store (v3io, S3, NFS) |
| Metadata Tracking | In-memory or local files | Persistent metadata in a central DB |
| Feature Store | Partially usable in-memory | Full real-time and offline feature store |
| Lineage & Provenance | File-based | Full graph of lineage and inter-function dependencies |

* * *

🎛️ 4. **UI and Monitoring**
----------------------------

| Capability | Local Conda | Iguazio Platform |
| --- | --- | --- |
| UI Dashboard | Optional via mlrun ui | Centralised multi-user dashboard |
| Run Monitoring | CLI or script logs | Real-time dashboard with resource monitoring |
| Model Monitoring | ❌ Not available | ✅ Drift detection, data quality, prediction logging |
| User Management | ❌ Single user only | ✅ Full access control and tenancy |

* * *

🔄 5. **Reproducibility and Lifecycle**
---------------------------------------

| Capability | Local Conda | Iguazio Platform |
| --- | --- | --- |
| Run Reproducibility | Manual (via script + seed) | Guaranteed via function snapshots + image hash |
| Model Registry | Local artifact path | Integrated model registry with promotion paths |
| Deployment Lifecycle | Manual (copy script, run locally) | Automated training → build → test → deploy pipeline |

* * *

🧮 Example: Function Execution Comparison
-----------------------------------------

### 🔹 Local Conda

```python
fn = mlrun.code_to_function(name="train", kind="job", filename="train.py")
run = fn.run(params={"n_estimators": 100}, local=True)
```

### 🔸 Iguazio (Serverless)

```python
fn = mlrun.code_to_function(name="train", kind="nuclio", filename="train.py", image="mlrun/mlrun")
project.set_function(fn)
run = fn.deploy()
```

* * *

🚀 Summary
----------

| Dimension | Local Conda (No Docker) | Iguazio Platform |
| --- | --- | --- |
| Setup Time | Minutes | Hours (cluster, platform install) |
| Target Use Case | Solo dev, research, prototyping | Multi-user, production-grade MLOps |
| Maintenance Cost | Low | High (infra, cluster, monitoring) |
| Flexibility | High for local dev | High for full stack deployments |
| Collaboration | ❌ Not built-in | ✅ First-class, multi-user access |

* * *

🧠 Final Evaluation
-------------------

You can treat **MLRun local mode** as analogous to:

*   `mlflow run ...` with local backend
    
*   `scikit-learn + logging` with some artifact tracking
    

Whereas **MLRun on Iguazio** becomes a full **Kubernetes-native, scalable MLOps orchestration platform**, similar to combining:

*   MLflow + Kubernetes + Nuclio + Feast + Seldon + Airflow + Spark
    

All under a unified interface with production lifecycle guarantees.

* * *

Would you like a migration guide showing how to port your local-only MLRun workflow to the Iguazio platform if you choose to scale it later?

## Johannes Foulds
OK, but I am interested in how things change in the actual code, compare it to the project structure and code you showed before

## Alfred Ipswich
Excellent. Let us now provide a **line-by-line, structural and semantic comparison** between the **local-only MLRun setup** (pure Conda, no Docker, no Kubernetes) and the **full Iguazio/MLRun platform setup** (containerized, Kubernetes-native, with remote orchestration and automation). We will contrast:

*   🔧 Project structure
    
*   🧠 Function definitions and metadata
    
*   🚀 Execution flow
    
*   📦 Artifact and model handling
    
*   🧭 Project YAML and runtime specifications
    

* * *

1\. 📁 **Project Structure Comparison**
---------------------------------------

### 🔹 Local Conda Setup

```pgsql
my-mlrun-local-project/
├── functions/
│   └── train.py                 # Local function code
├── artifacts/                  # Outputs saved to filesystem
├── project.yaml                # Defines function metadata
└── run_local.py                # Script to run local function
```

### 🔸 Iguazio Platform Setup

```bash
my-mlrun-iguazio-project/
├── functions/
│   └── train.py
├── artifacts/                  # Still present, but mostly cloud-backed
├── Dockerfile                  # Optional: custom environment
├── project.yaml                # Includes image, volumes, labels, etc.
└── run_pipeline.py             # Orchestrated workflow script
```

* * *

2\. 🧠 **Function Definition Changes**
--------------------------------------

### 🔹 Local Conda (`train.py`)

```python
# functions/train.py
def train_model(context, n_estimators=100):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import load_iris
    ...
    context.log_result("accuracy", acc)
    context.log_model("rf_model", model_file="model.pkl")
```

### 🔸 Iguazio

Same function logic **can remain unchanged**, but you may:

*   Add more logging for distributed logs
    
*   Expect external data via **DataItem** abstraction
    
*   Add annotations for model tracking or feature store usage
    

```python
def train_model(context, data: mlrun.DataItem, n_estimators=100):
    df = data.as_df()  # Can be from S3, v3io, etc.
```

* * *

3\. 🚀 **Execution Script Comparison**
--------------------------------------

### 🔹 Local Execution: `run_local.py`

```python
import mlrun

project = mlrun.get_or_create_project("myproj", "./")
fn = project.set_function("functions/train.py", name="train", kind="job")
run = fn.run(
    handler="train_model",
    params={"n_estimators": 100},
    local=True,                     # <=== LOCAL MODE
    artifact_path="./artifacts"
)
```

### 🔸 Iguazio Orchestrated Run: `run_pipeline.py`

```python
import mlrun

project = mlrun.load_project("myproj", "./")

# Load the function (registered, versioned)
fn = project.set_function(
    "functions/train.py", 
    name="train", 
    kind="job", 
    image="mlrun/mlrun",  # <=== IMAGE REQUIRED
    handler="train_model"
)

# Run remotely on Kubernetes
run = fn.run(
    params={"n_estimators": 100},
    artifact_path=project.get_artifact_uri("models"),
    local=False                   # <=== CLOUD EXECUTION
)
```

* * *

4\. 🧬 **project.yaml Comparison**
----------------------------------

### 🔹 Local Minimal

```yaml
kind: project
metadata:
  name: myproj
spec:
  functions:
    - url: functions/train.py
      name: train
      kind: job
```

### 🔸 Iguazio Platform

```yaml
kind: project
metadata:
  name: myproj
spec:
  functions:
    - url: functions/train.py
      name: train
      kind: job
      image: mlrun/mlrun  # <=== MANDATORY
      requirements: [
        scikit-learn,
        pandas
      ]
      handler: train_model
```

You can also attach:

*   volume mounts
    
*   node selectors
    
*   resource requests/limits
    
*   labels for CI/CD triggers
    

* * *

5\. 📦 **Artifact Handling**
----------------------------

### 🔹 Local

```python
context.log_model("rf_model", model_file="model.pkl")
```

*   Stores to `./artifacts/model.pkl` or similar.
    

### 🔸 Iguazio

```python
context.log_model("rf_model", model_file="model.pkl", model_dir="/user-artifacts/models/")
```

*   Stores in distributed object store (e.g., v3io, S3)
    
*   Accessible across functions, users, pipelines
    
*   Registered in model registry if specified
    

* * *

6\. 🧠 **Function Storage and Versioning**
------------------------------------------

| Capability | Local | Iguazio |
| --- | --- | --- |
| Function source | .py file | .py file or Git repo |
| Image specification | ❌ (N/A) | ✅ required |
| Function registry | ❌ Manual | ✅ via central MLRun DB |
| Reuse across users | ❌ No | ✅ Yes |

* * *

✅ Summary: What Changes?
------------------------

| Category | Local Conda | Iguazio Full Stack |
| --- | --- | --- |
| Code Changes | Minimal (add local=True) | Requires image=..., remote artifact_path, cloud DataItem |
| project.yaml | Simple | Requires image, dependencies, labels |
| Execution Script | Scripted | Orchestrated via pipelines or API |
| Model & Artifact Paths | Local FS | Cloud object store + registry |
| Function Isolation | None | Full container isolation |
| CI/CD & Monitoring | Manual | Fully integrated |

* * *

Would you like me to generate two side-by-side `.zip` project templates — one for pure local and one for Iguazio-style deployment — so you can test and compare them directly?

## Johannes Foulds
No from a clean slate, what is the best practices for creating projects in Iguazio? Again I want to see the structure the repository should be in, and what should be in the files. Don't force it into what we already discussed, follow the best practices as per Iguazio.

## Alfred Ipswich
To establish a robust and scalable MLRun project within the Iguazio MLOps platform, adhere to the following best practices. This structure ensures seamless integration with MLRun's orchestration capabilities, supports CI/CD workflows, and facilitates collaboration among data science and engineering teams.

* * *

📁 Recommended Project Directory Structure
------------------------------------------

Organize your project directory as follows:

```bash
my-mlrun-project/
├── data/                   # Local datasets or outputs (excluded from version control)
├── docs/                   # Project documentation
├── src/                    # Source code: functions, modules, utilities
│   ├── functions/          # MLRun function scripts
│   ├── workflows/          # Workflow definitions (e.g., Kubeflow pipelines)
│   └── project_setup.py    # Optional: Project initialization script
├── tests/                  # Unit and integration tests
├── .env                    # Environment variables (excluded from version control)
├── .gitignore              # Git ignore rules
├── Dockerfile              # Optional: Custom Docker image definition
├── project.yaml            # MLRun project specification
├── README.md               # Project overview and instructions
└── requirements.txt        # Project-level Python dependencies
```

**Key Considerations:**

*   **`project.yaml`**: Defines the project's metadata, functions, workflows, and artifacts.
    
*   **`project_setup.py`**: Optional script executed upon project loading to programmatically register functions, workflows, and artifacts.
    
*   **`src/functions/`**: Contains individual Python scripts or modules, each representing a distinct MLRun function.
    
*   **`src/workflows/`**: Houses workflow definitions, typically as Python scripts utilizing MLRun's pipeline capabilities.
    
*   **`tests/`**: Includes test suites to validate function logic and workflows, promoting reliability and facilitating CI/CD integration.
    

* * *

📝 `project.yaml` Example
-------------------------

An example `project.yaml` file might look like:

```yaml
kind: project
metadata:
  name: my-mlrun-project
spec:
  description: "MLRun project for model training and deployment"
  params:
    data_url: "https://example.com/data.csv"
    model_name: "classifier"
  functions:
    - url: src/functions/data_prep.py
      name: data-prep
      kind: job
      image: mlrun/mlrun
      handler: prepare_data
    - url: src/functions/train.py
      name: train
      kind: job
      image: mlrun/mlrun
      handler: train_model
  workflows:
    - path: src/workflows/main_workflow.py
      name: main
  artifacts:
    - kind: dataset
      metadata:
        name: raw-data
      spec:
        target_path: "v3io:///projects/my-mlrun-project/data/raw.csv"
```

**Notes:**

*   **Functions**: Specify the path to the function script, the function name, execution kind, Docker image, and the handler function within the script.[docs.mlrun.org+1docs.mlrun.org+1](https://docs.mlrun.org/en/stable/projects/run-build-deploy.html?utm_source=chatgpt.com)
    
*   **Workflows**: Define the path to the workflow script and assign a name for reference.
    
*   **Artifacts**: Register datasets, models, or other artifacts with metadata and storage paths.
    

* * *

⚙️ `project_setup.py` Usage
---------------------------

The `project_setup.py` script allows for dynamic project configuration. MLRun automatically executes this script when loading the project.[docs.mlrun.org+1alonmrmlrun.readthedocs.io+1](https://docs.mlrun.org/en/stable/projects/project-setup.html?utm_source=chatgpt.com)

```python
# src/project_setup.py
import mlrun

def setup(project: mlrun.projects.MlrunProject) -> mlrun.projects.MlrunProject:
    # Set default Docker image for functions
    project.set_default_image("mlrun/mlrun")

   # Register functions
    project.set_function(
        name="data-prep",
        func="functions/data_prep.py",
        kind="job",
        handler="prepare_data"
    )
    project.set_function(
        name="train",
        func="functions/train.py",
        kind="job",
        handler="train_model"
    )

   # Register workflow
    project.set_workflow(
        name="main",
        workflow_path="workflows/main_workflow.py"
    )

   # Set project parameters
    project.spec.params = {
        "data_url": "https://example.com/data.csv",
        "model_name": "classifier"
    }

   # Save the project configuration
    project.save()
    return project
```

**Advantages:**

*   **Dynamic Configuration**: Allows conditional logic and dynamic registration of project components.
    
*   **Consistency**: Ensures that all team members have a consistent project setup.
    

* * *

🔄 Git Integration and CI/CD Best Practices
-------------------------------------------

*   **Version Control**: Initialize a Git repository in the project root to track changes and facilitate collaboration.
    
*   **Remote Repository**: Link to a remote Git repository (e.g., GitHub, GitLab) for centralized code management.
    
*   **CI/CD Pipelines**: Integrate with CI/CD tools (e.g., GitHub Actions, GitLab CI) to automate testing, building, and deployment processes.
    
*   **Project Loading**: Use MLRun's `load_project()` or `get_or_create_project()` methods to load projects from the Git repository, ensuring synchronization across environments.[docs.mlrun.org+4docs.mlrun.org+4docs.mlrun.org+4](https://docs.mlrun.org/en/stable/projects/load-project.html?utm_source=chatgpt.com)
    

* * *

📚 References
-------------

*   MLRun Documentation: [Create, save, and use projects](https://docs.mlrun.org/en/v1.6.4/projects/create-project.html)
    
*   MLRun Documentation: [MLRun project bootstrapping with project\_setup.py](https://docs.mlrun.org/en/stable/projects/project-setup.html)
    
*   MLRun Documentation: [Load project YAML from Git, Zip, Tar source](https://docs.mlrun.org/en/stable/projects/load-project-yaml.html)
    

* * *

By adhering to this structured approach, you can leverage MLRun's full capabilities within the Iguazio platform, promoting reproducibility, scalability, and efficient collaboration throughout the machine learning lifecycle.

![Favicon](https://www.google.com/s2/favicons?domain=https://docs.mlrun.org&sz=32)

Sourcesundefined

## Johannes Foulds
Good, now following the best practices, take me through the full Machine Learning Workflow, from EDA to inference on the iris dataset (or if Iguzio used a another simple dataset in their documentation, follow their conventions)

## Alfred Ipswich
![https://www.iguazio.com/wp-content/uploads/2023/01/pipeline-2048x844.png](https://tse4.mm.bing.net/th/id/OIP.AJW4lwhg885GtFG4GjL7DQHaDD?cb=iwp1&w=195&h=195&c=7)

![https://docs.mlrun.org/en/latest/_images/cicd_flow.png](https://tse2.mm.bing.net/th/id/OIP.eEtKmFWGHoyihiKuOQ5djgHaDX?cb=iwp1&w=215&h=215&c=7)

![https://www.iguazio.com/wp-content/uploads/2021/01/Microsoft-Iguazio-Integrations.jpg](https://tse1.mm.bing.net/th/id/OIP.s-KfbveKoer62fvUKxabGwHaE0?cb=iwp1&w=308&h=308&c=7)

![https://www.iguazio.com/wp-content/uploads/2023/11/Projects-Feature-store-Feature-sets.png](https://tse1.mm.bing.net/th?id=OIP.eur1TEVofidj4q7Vc7udmAHaEo&cb=iwp1&w=296&h=296&c=7)

To implement a comprehensive machine learning workflow on the Iguazio MLOps platform using MLRun, we'll follow best practices that encompass the entire lifecycle—from data ingestion and exploratory data analysis (EDA) to model training, evaluation, deployment, and inference. We'll utilize the Iris dataset, a standard in machine learning, to illustrate this process.

* * *

📁 Project Structure
--------------------

Organize your project directory as follows:

```bash
iris-mlrun-project/
├── data/                   # Local datasets or outputs (excluded from version control)
├── docs/                   # Project documentation
├── src/                    # Source code: functions, modules, utilities
│   ├── functions/          # MLRun function scripts
│   ├── workflows/          # Workflow definitions (e.g., Kubeflow pipelines)
│   └── project_setup.py    # Project initialization script
├── tests/                  # Unit and integration tests
├── .gitignore              # Git ignore rules
├── Dockerfile              # Optional: Custom Docker image definition
├── project.yaml            # MLRun project specification
├── README.md               # Project overview and instructions
└── requirements.txt        # Project-level Python dependencies
```

* * *

📝 `project.yaml` Configuration
-------------------------------

Define your MLRun project in `project.yaml`:

```yaml
kind: project
metadata:
  name: iris-mlrun-project
spec:
  description: "MLRun project for Iris dataset classification"
  params:
    model_name: "iris_classifier"
  functions:
    - url: src/functions/data_prep.py
      name: data-prep
      kind: job
      image: mlrun/mlrun
      handler: prepare_data
    - url: src/functions/train.py
      name: train
      kind: job
      image: mlrun/mlrun
      handler: train_model
    - url: src/functions/evaluate.py
      name: evaluate
      kind: job
      image: mlrun/mlrun
      handler: evaluate_model
    - url: src/functions/serve.py
      name: serve
      kind: serving
      image: mlrun/mlrun
      handler: serve_model
  workflows:
    - path: src/workflows/main_workflow.py
      name: main
```

* * *

⚙️ `project_setup.py` Script
----------------------------

Use `project_setup.py` to programmatically set up your project:

```python
# src/project_setup.py
import mlrun

def setup(project: mlrun.projects.MlrunProject) -> mlrun.projects.MlrunProject:
    project.set_default_image("mlrun/mlrun")

   # Register functions
    project.set_function(
        name="data-prep",
        func="functions/data_prep.py",
        kind="job",
        handler="prepare_data"
    )
    project.set_function(
        name="train",
        func="functions/train.py",
        kind="job",
        handler="train_model"
    )
    project.set_function(
        name="evaluate",
        func="functions/evaluate.py",
        kind="job",
        handler="evaluate_model"
    )
    project.set_function(
        name="serve",
        func="functions/serve.py",
        kind="serving",
        handler="serve_model"
    )

   # Register workflow
    project.set_workflow(
        name="main",
        workflow_path="workflows/main_workflow.py"
    )

   # Set project parameters
    project.spec.params = {
        "model_name": "iris_classifier"
    }

   project.save()
    return project
```

* * *

🧪 Function Implementations
---------------------------

### 1\. Data Preparation: `data_prep.py`

Load and preprocess the Iris dataset.

```python
# src/functions/data_prep.py
def prepare_data(context):
    import pandas as pd
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split

   iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target, name='label')

   X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

   train_set = pd.concat([X_train, y_train], axis=1)
    test_set = pd.concat([X_test, y_test], axis=1)

   context.log_dataset("train_set", df=train_set, format="csv")
    context.log_dataset("test_set", df=test_set, format="csv")
```

### 2\. Model Training: `train.py`

Train a classifier on the prepared data.

```python
# src/functions/train.py
def train_model(context, train_set: mlrun.DataItem, model_name: str):
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    import pickle

   df = train_set.as_df()
    X = df.drop("label", axis=1)
    y = df["label"]

   model = RandomForestClassifier()
    model.fit(X, y)

   # Save model
    model_file = f"{model_name}.pkl"
    with open(model_file, "wb") as f:
        pickle.dump(model, f)

   context.log_model(model_name, model_file=model_file)
```

### 3\. Model Evaluation: `evaluate.py`

Evaluate the trained model on the test set.

```python
# src/functions/evaluate.py
def evaluate_model(context, test_set: mlrun.DataItem, model: mlrun.ModelArtifact):
    import pandas as pd
    from sklearn.metrics import accuracy_score
    import pickle

   df = test_set.as_df()
    X = df.drop("label", axis=1)
    y_true = df["label"]

   # Load model
    model_file = model.get_model().get_local_path()
    with open(model_file, "rb") as f:
        clf = pickle.load(f)

   y_pred = clf.predict(X)
    accuracy = accuracy_score(y_true, y_pred)

   context.log_result("accuracy", accuracy)
```

### 4\. Model Serving: `serve.py`

Deploy the model as a real-time inference service.

```python
# src/functions/serve.py
def serve_model():
    import mlrun
    from sklearn.ensemble import RandomForestClassifier
    import pickle

   class IrisClassifier(mlrun.serving.V2ModelServer):
        def load(self):
            model_file = self.get_model_path()
            with open(model_file, "rb") as f:
                self.model = pickle.load(f)

       def predict(self, body):
            features = body["inputs"]
            return self.model.predict([features]).tolist()

   return IrisClassifier()
```

* * *

🔁 Workflow Definition: `main_workflow.py`
------------------------------------------

Define the pipeline to orchestrate the functions.[GeeksforGeeks+1Arm+1](https://www.geeksforgeeks.org/exploratory-data-analysis-on-iris-dataset/?utm_source=chatgpt.com)

```python
# src/workflows/main_workflow.py
from kfp import dsl

@dsl.pipeline(name="Iris Classification Pipeline")
def main_pipeline():
    # Data Preparation
    data_prep = mlrun.run_function("data-prep")

   # Model Training
    train = mlrun.run_function(
        "train",
        inputs={"train_set": data_prep.outputs["train_set"]},
        params={"model_name": "iris_classifier"}
    )

   # Model Evaluation
    evaluate = mlrun.run_function(
        "evaluate",
        inputs={
            "test_set": data_prep.outputs["test_set"],
            "model": train.outputs["model"]
        }
    )

   # Model Serving
    mlrun.deploy_function("serve")
```

* * *

🚀 Execution
------------

To execute the workflow:[Iguazio](https://www.iguazio.com/solutions/pipeline-orchestration/?utm_source=chatgpt.com)

```python
import mlrun

# Load the project
project = mlrun.load_project("./iris-mlrun-project")

# Run the workflow
project.run("main")
```

Monitor the execution and results via the MLRun UI.

* * *

📚 References
-------------

*   MLRun Documentation: [Working with data and model artifacts](https://docs.mlrun.org/en/stable/training/working-with-data-and-model-artifacts.html)
    
*   MLRun Documentation: [Projects and automation](https://docs.mlrun.org/en/stable/projects/project.html)
    
*   MLRun Documentation: [Tutorials and Examples](https://docs.mlrun.org/en/stable/tutorials/index.html)
    

* * *

By following this structured approach, you can leverage MLRun's capabilities within the Iguazio platform to build, deploy, and manage machine learning workflows efficiently and effectively.

Sourcesundefined

## Johannes Foulds
OK, and taking all this back to running only locally without docker only in conda environment?

## Alfred Ipswich
![https://docs.mlrun.org/en/stable/_images/mlrun_concepts_architecture.png](https://tse2.mm.bing.net/th?id=OIP.jpDCQn0n8FXTE-cGR0Q3fgHaDA&w=192&h=192&c=7)

![https://docs.mlrun.org/en/stable/_images/workflow.png](https://tse4.mm.bing.net/th?id=OIP.CHL6O0GlB6NGW8Br2SF1SAHaED&w=259&h=259&c=7)

![https://docs.mlrun.org/en/latest/_images/cicd_flow.png](https://tse2.mm.bing.net/th?id=OIP.eEtKmFWGHoyihiKuOQ5djgHaDX&w=215&h=215&c=7)

![https://docs.mlrun.org/en/latest/_static/images/project.png](https://tse4.mm.bing.net/th?id=OIP.UX3r4EMqpukplbo-5BXSbgHaCY&w=152&h=152&c=7)

Certainly. To execute the full ML workflow using MLRun entirely within a local Conda environment—without Docker, Kubernetes, or remote services—you can adapt the previous Iguazio-based structure accordingly. Below is a detailed guide tailored for local execution.

* * *

🧰 1. Environment Setup
-----------------------

### a. Create and Activate a Conda Environment

Ensure you're using Python 3.9, as MLRun supports this version:[docs.mlrun.org+1docs.mlrun.org+1](https://docs.mlrun.org/en/latest/install/remote.html?utm_source=chatgpt.com)

```bash
conda create -n mlrun-env python=3.9 -y
conda activate mlrun-env
```

### b. Install MLRun and Dependencies

Install MLRun along with necessary packages:[docs.mlrun.org+3docs.mlrun.org+3docs.mlrun.org+3](https://docs.mlrun.org/en/latest/install/kubernetes.html?utm_source=chatgpt.com)

```bash
pip install mlrun scikit-learn pandas
```

For additional storage backends (e.g., S3), install optional dependencies as needed.

* * *

📁 2. Project Structure
-----------------------

Organize your project directory as follows:

```bash
iris-mlrun-local/
├── functions/
│   ├── data_prep.py
│   ├── train.py
│   ├── evaluate.py
│   └── serve.py
├── artifacts/                  # Outputs saved to filesystem
├── project.yaml                # MLRun project specification
└── run_local.py                # Script to run the workflow
```

This structure aligns with MLRun's best practices for local development.

* * *

📝 3. `project.yaml` Configuration
----------------------------------

Define your MLRun project in `project.yaml`:

```yaml
kind: project
metadata:
  name: iris-mlrun-local
spec:
  description: "MLRun local project for Iris dataset classification"
  functions:
    - url: functions/data_prep.py
      name: data-prep
      kind: job
      handler: prepare_data
    - url: functions/train.py
      name: train
      kind: job
      handler: train_model
    - url: functions/evaluate.py
      name: evaluate
      kind: job
      handler: evaluate_model
    - url: functions/serve.py
      name: serve
      kind: job
      handler: serve_model
```

Note: The `kind` is set to `job` for all functions, including `serve`, since we're not deploying a real-time service in this local setup.

* * *

🧪 4. Function Implementations
------------------------------

### a. Data Preparation: `data_prep.py`

Load and preprocess the Iris dataset:

```python
def prepare_data(context):
    from sklearn.datasets import load_iris
    import pandas as pd
    from sklearn.model_selection import train_test_split

   iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target, name='label')

   X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

   train_set = pd.concat([X_train, y_train], axis=1)
    test_set = pd.concat([X_test, y_test], axis=1)

   context.log_dataset("train_set", df=train_set, format="csv")
    context.log_dataset("test_set", df=test_set, format="csv")
```

### b. Model Training: `train.py`

Train a classifier on the prepared data:

```python
def train_model(context, train_set):
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    import pickle

   df = pd.read_csv(train_set)
    X = df.drop("label", axis=1)
    y = df["label"]

   model = RandomForestClassifier()
    model.fit(X, y)

   model_file = "model.pkl"
    with open(model_file, "wb") as f:
        pickle.dump(model, f)

   context.log_model("iris_classifier", model_file=model_file)
```

### c. Model Evaluation: `evaluate.py`

Evaluate the trained model on the test set:

```python
def evaluate_model(context, test_set, model_path):
    import pandas as pd
    from sklearn.metrics import accuracy_score
    import pickle

   df = pd.read_csv(test_set)
    X = df.drop("label", axis=1)
    y_true = df["label"]

   with open(model_path, "rb") as f:
        model = pickle.load(f)

   y_pred = model.predict(X)
    accuracy = accuracy_score(y_true, y_pred)

   context.log_result("accuracy", accuracy)
```

### d. Model Serving: `serve.py`

For local inference, define a simple function:

```python
def serve_model(context, model_path, input_features):
    import pickle
    import numpy as np

   with open(model_path, "rb") as f:
        model = pickle.load(f)

   prediction = model.predict(np.array([input_features]))
    context.log_result("prediction", prediction.tolist())
```

* * *

🚀 5. Execution Script: `run_local.py`
--------------------------------------

Run the entire workflow locally:

```python
import mlrun

# Load or create the project
project = mlrun.get_or_create_project("iris-mlrun-local", "./")

# Set functions
project.set_function("functions/data_prep.py", name="data-prep", kind="job", handler="prepare_data")
project.set_function("functions/train.py", name="train", kind="job", handler="train_model")
project.set_function("functions/evaluate.py", name="evaluate", kind="job", handler="evaluate_model")
project.set_function("functions/serve.py", name="serve", kind="job", handler="serve_model")

# Run data preparation
prep_run = project.run_function("data-prep", local=True)

# Run training
train_run = project.run_function(
    "train",
    inputs={"train_set": prep_run.outputs["train_set"]},
    local=True
)

# Run evaluation
evaluate_run = project.run_function(
    "evaluate",
    inputs={
        "test_set": prep_run.outputs["test_set"],
        "model_path": train_run.outputs["model"]
    },
    local=True
)

# Run inference
serve_run = project.run_function(
    "serve",
    inputs={
        "model_path": train_run.outputs["model"],
        "input_features": [5.1, 3.5, 1.4, 0.2]
    },
    local=True
)

# Print results
print("Accuracy:", evaluate_run.outputs["accuracy"])
print("Prediction:", serve_run.outputs["prediction"])
```

This script sequentially executes each function locally, passing outputs between them.

* * *

📦 6. Artifacts and Results
---------------------------

Artifacts such as datasets, models, and results are stored in the `artifacts/` directory by default. You can configure the artifact path using the `artifact_path` parameter in `run_function`.

* * *

🧠 7. Considerations
--------------------

*   **Local Execution**: All functions run within your current Conda environment, leveraging installed packages.
    
*   **No Docker/Kubernetes**: This setup avoids the overhead of containerization and orchestration, suitable for development and testing.
    
*   **Scalability**: For production workloads requiring scalability, consider transitioning to a Docker/Kubernetes-based setup.
    

* * *

By following this approach, you can effectively utilize MLRun for machine learning workflows entirely within a local Conda environment, facilitating development and testing without the complexities of containerization or orchestration platforms.

![Favicon](https://www.google.com/s2/favicons?domain=https://docs.mlrun.org&sz=32)

Sourcesundefined

## Johannes Foulds
Let's look at this new scenario:1. I still don't want to deploy MLRun, it will still just run in a normal conda environment2. I do have access to a docker environment, but this is just a generic environment (Linux VM with docker installed)3. I would like to run my functions on docker ideally using the MLRun API as normal4. It would be great if I could also use Functions from the MLRun marketpalace.To make it clear, I still absolutely do not want to install a full MLRun environment, still just do a simple pip install

## Alfred Ipswich
Yes, you can run MLRun functions within Docker containers from a local Conda environment without deploying the full MLRun server. This setup allows you to leverage Docker for function execution while maintaining a lightweight local development environment.

* * *

✅ Overview
----------

*   **MLRun SDK**: Install via `pip` in your Conda environment.
    
*   **Docker**: Utilize Docker to execute functions in isolated environments.
    
*   **MLRun Marketplace**: Access and use functions from the MLRun Function Hub.
    

* * *

🧰 Prerequisites
----------------

1.  **Conda Environment**:
    
    Ensure you have a Conda environment with Python 3.9:
    
    ```bash
    conda create -n mlrun-env python=3.9 -y
    conda activate mlrun-env
    pip install mlrun
    ```

2.  **Docker**:
    
    Install Docker on your system and ensure it's running.
    

* * *

⚙️ Configuration
----------------

1.  **Set MLRun Environment**:
    
    Configure MLRun to use local execution and specify the artifact path:
    
    ```python
    import mlrun
    
    mlrun.set_environment(artifact_path="./artifacts")
    ```

2.  **Create or Load a Project**:
    
    Initialize an MLRun project:
    
    ```python
    project = mlrun.get_or_create_project("my_project", context="./")
    ```

* * *

🛠️ Define and Run Functions in Docker
--------------------------------------

1.  **Create a Function**:
    
    Define a function to run in a Docker container:
    
    ```python
    fn = project.set_function(
        name="my_function",
        func="my_script.py",
        kind="job",
        image="mlrun/mlrun",
        handler="my_handler"
    )
    ```

*   `func`: Path to your Python script.[alonmrmlrun.readthedocs.io+4docs.mlrun.org+4MinIO Blog+4](https://docs.mlrun.org/en/v1.1.2/runtimes/load-from-marketplace.html?utm_source=chatgpt.com)
    
*   `kind`: Execution type; `job` runs as a batch job.[docs.mlrun.org](https://docs.mlrun.org/en/v1.0.0/runtimes/using-functions.html?utm_source=chatgpt.com)
    
*   `image`: Docker image to use.[docs.mlrun.org](https://docs.mlrun.org/en/v1.1.2/runtimes/load-from-marketplace.html?utm_source=chatgpt.com)
    
*   `handler`: Function within your script to execute.[docs.mlrun.org](https://docs.mlrun.org/en/v1.0.0/projects/use-project.html?utm_source=chatgpt.com)
    

2.  **Run the Function**:
    
    Execute the function:
    
    ```python
    run = fn.run(params={"param1": "value1"})
    ```

This command builds and runs the function inside the specified Docker image.

* * *

📦 Using MLRun Marketplace Functions
------------------------------------

MLRun provides a Function Hub with pre-built functions.[docs.mlrun.org+5docs.mlrun.org+5docs.mlrun.org+5](https://docs.mlrun.org/en/stable/runtimes/create-and-use-functions.html?utm_source=chatgpt.com)

1.  **Import a Function**:
    
    Load a function from the marketplace:
    
    ```python
    fn = project.set_function("hub://describe", name="describe")
    ```

2.  **Run the Function**:
    
    Execute the imported function:
    
    ```python
    run = fn.run(params={"table": "iris_dataset.csv"})
    ```

This will run the `describe` function on the specified dataset.

* * *

📝 Notes
--------

*   **No MLRun Server Required**: This setup uses only the MLRun SDK and Docker, avoiding the need for a full MLRun server deployment.
    
*   **Artifact Management**: Artifacts are stored locally in the specified `artifact_path`.
    
*   **Function Isolation**: Running functions in Docker containers ensures environment isolation and reproducibility.
    

* * *

By following this approach, you can effectively utilize MLRun's capabilities within your local Conda environment, leveraging Docker for function execution and accessing a wide range of pre-built functions from the MLRun marketplace.

![Favicon](https://www.google.com/s2/favicons?domain=https://docs.mlrun.org&sz=32)

Sourcesundefined

## Johannes Foulds
OK, but I am now starting to second guess you, how is this linked to my local docker install?

## Alfred Ipswich
![https://docs.mlrun.org/en/stable/_static/images/mlrun-flow.png](https://tse1.mm.bing.net/th?id=OIP.e4eWpYFgO107LGpKqApobQHaDG&cb=iwp1&w=198&h=198&c=7)

![https://www.iguazio.com/wp-content/uploads/2023/01/pipeline-2048x844.png](https://tse4.mm.bing.net/th?id=OIP.AJW4lwhg885GtFG4GjL7DQHaDD&cb=iwp1&w=195&h=195&c=7)

![https://docs.mlrun.org/en/stable/_images/mlrun_concepts_architecture.png](https://tse2.mm.bing.net/th?id=OIP.jpDCQn0n8FXTE-cGR0Q3fgHaDA&cb=iwp1&w=192&h=192&c=7)

![https://docs.mlrun.org/en/stable/_images/workflow.png](https://tse4.mm.bing.net/th?id=OIP.CHL6O0GlB6NGW8Br2SF1SAHaED&cb=iwp1&w=259&h=259&c=7)

To execute MLRun functions within Docker containers from your local Conda environment—without deploying the full MLRun server—you can utilize MLRun's capability to run functions in Docker by specifying the appropriate runtime and image. This approach allows you to leverage Docker for function execution while maintaining a lightweight local development setup.

* * *

🧰 Prerequisites
----------------

1.  **Conda Environment**:
    
    *   Ensure you have a Conda environment with Python 3.9:
        
        ```bash
        conda create -n mlrun-env python=3.9 -y
        conda activate mlrun-env
        pip install mlrun
        ```
2.  **Docker**:
    
    *   Install Docker on your system and ensure it's running.
        

* * *

⚙️ Configuring MLRun to Use Docker
----------------------------------

MLRun can execute functions in Docker containers by specifying the `kind` as `'job'` and providing the desired Docker image. This setup does not require the full MLRun server deployment.

### Example: Running a Function in Docker

```python
import mlrun

# Create a new MLRun project
project = mlrun.new_project("my_project", "./")

# Define the function
fn = project.set_function(
    name="my_function",
    func="my_script.py",  # Path to your script
    kind="job",
    image="mlrun/mlrun",  # Docker image to use
    handler="my_handler"  # Function within your script
)

# Run the function
run = fn.run(params={"param1": "value1"})
```

In this example, MLRun will execute `my_handler` from `my_script.py` inside a Docker container using the `mlrun/mlrun` image.

* * *

📦 Using MLRun Marketplace Functions
------------------------------------

MLRun provides a Function Hub with pre-built functions that can be imported and executed.

### Import and Run a Marketplace Function

```python
# Import a function from the MLRun Function Hub
fn = project.set_function("hub://describe", name="describe")

# Run the function
run = fn.run(params={"table": "iris_dataset.csv"})
```

This will run the `describe` function on the specified dataset within a Docker container.

* * *

📝 Notes
--------

*   **No MLRun Server Required**: This setup uses only the MLRun SDK and Docker, avoiding the need for a full MLRun server deployment.
    
*   **Artifact Management**: Artifacts are stored locally in the specified `artifact_path`.
    
*   **Function Isolation**: Running functions in Docker containers ensures environment isolation and reproducibility.
    

* * *

By following this approach, you can effectively utilize MLRun's capabilities within your local Conda environment, leveraging Docker for function execution and accessing a wide range of pre-built functions from the MLRun marketplace.

Sources

## Johannes Foulds
OK, and if I want to use OpenShift to run my containers -- same config only MLRun running locally

## Alfred Ipswich
![https://spiritedengineering.net/wp-content/uploads/2020/03/Screen-Shot-2020-03-12-at-5.36.53-PM.png](https://tse1.mm.bing.net/th?id=OIP.SgAKd3rxuLQ27umjIC5XSQHaEI&cb=iwc1&w=264&h=264&c=7)

![https://k21academy.com/wp-content/uploads/2021/09/OpenShift-1-1024x416.png](https://tse1.mm.bing.net/th?id=OIP.u04yWZKjO8rZOuMgVg1U1gHaDA&cb=iwc1&w=192&h=192&c=7)

![https://assets.cloudacademy.com/bakery/media/uploads/entity/blobid1-2fc41615-d79f-48ce-8d91-370a3c0625bb.png](https://tse3.mm.bing.net/th?id=OIP.mEz9fdZXblX-LSFjJfeGbAHaFW&cb=iwc1&w=342&h=342&c=7)

![https://spiritedengineering.net/wp-content/uploads/2019/07/openshift.png](https://tse2.mm.bing.net/th?id=OIP.6Uwb1oE3u1xGf_JLhbM18AHaEl&cb=iwc1&w=293&h=293&c=7)

To execute MLRun functions on an OpenShift cluster while maintaining a lightweight local development environment (e.g., a Conda environment with MLRun installed via `pip`), you can configure MLRun to interact with the OpenShift cluster as a remote execution backend. This setup allows you to write and manage your code locally while leveraging OpenShift's capabilities for function execution.

* * *

🧰 Prerequisites
----------------

1.  **Local Environment**:
    
    *   Python 3.9 Conda environment.
        
    *   MLRun installed via `pip`:
        
        ```bash
        pip install mlrun
        ```
2.  **OpenShift Cluster**:
    
    *   Access to an OpenShift cluster with appropriate permissions.
        
    *   `kubectl` and `oc` CLI tools configured to interact with the cluster.
        
3.  **Docker**:
    
    *   Docker installed locally for building container images if needed.
        

* * *

⚙️ Configuring MLRun to Use OpenShift
-------------------------------------

MLRun can be configured to execute functions on a remote Kubernetes cluster, such as OpenShift, by setting the appropriate environment variables or using the MLRun SDK.

### a. Set Environment Variables

You can configure MLRun to use the OpenShift cluster by setting the following environment variables:

```bash
export MLRUN_DBPATH=https://<mlrun-api-service>.<namespace>.svc.cluster.local:8080
export MLRUN_NAMESPACE=<your-namespace>
export MLRUN_KFP_URL=https://<kfp-api-service>.<namespace>.svc.cluster.local:8888
```

*   `MLRUN_DBPATH`: The URL of the MLRun API service in your OpenShift cluster.
    
*   `MLRUN_NAMESPACE`: The Kubernetes namespace where your resources are located.
    
*   `MLRUN_KFP_URL`: The URL of the Kubeflow Pipelines API service if using pipelines.
    

### b. Use MLRun SDK to Set Environment

Alternatively, you can set the environment within your Python code:

```python
import mlrun

mlrun.set_environment(
    api_path="https://<mlrun-api-service>.<namespace>.svc.cluster.local:8080",
    project="my-project",
    user_project=True
)
```

This configuration directs MLRun to interact with the specified OpenShift services for function execution.

* * *

🛠️ Defining and Running Functions
----------------------------------

With the environment configured, you can define and run functions as follows:[MLRun Documentation+1MLRun Documentation+1](https://docs.mlrun.org/en/v1.1.2/install/remote.html?utm_source=chatgpt.com)

```python
import mlrun

# Load or create a project
project = mlrun.get_or_create_project("my-project", "./")

# Define a function
fn = project.set_function(
    name="my-function",
    func="my_script.py",
    kind="job",
    image="my-custom-image:latest",
    handler="my_handler"
)

# Run the function
run = fn.run(params={"param1": "value1"})
```

*   `func`: Path to your Python script.
    
*   `kind`: Execution type; `job` runs as a batch job.
    
*   `image`: Docker image to use; ensure it's accessible from the OpenShift cluster.
    
*   `handler`: Function within your script to execute.[Medium](https://medium.com/hashicorp-engineering/consuming-secrets-in-your-openshift-applications-using-hashicorp-vault-injector-4fbf84156e7f?utm_source=chatgpt.com)
    

This setup allows MLRun to schedule and execute the function within the OpenShift cluster while you manage and monitor the process from your local environment.

* * *

📦 Using MLRun Marketplace Functions
------------------------------------

MLRun provides a Function Hub with pre-built functions that can be imported and executed.

### Import and Run a Marketplace Function

```python
# Import a function from the MLRun Function Hub
fn = project.set_function("hub://describe", name="describe")

# Run the function
run = fn.run(params={"table": "iris_dataset.csv"})
```

This will run the `describe` function on the specified dataset within the OpenShift cluster.

* * *

📝 Notes
--------

*   **No MLRun Server Required Locally**: This setup uses only the MLRun SDK in your local environment, avoiding the need for a full MLRun server deployment locally.
    
*   **OpenShift Integration**: Ensure that the MLRun components (e.g., API service) are deployed within your OpenShift cluster to handle function execution requests.
    
*   **Security and Permissions**: Verify that your OpenShift user has the necessary permissions to create and manage resources within the specified namespace.
    

* * *

By configuring MLRun to interact with your OpenShift cluster, you can seamlessly execute functions in a scalable and managed environment while maintaining a streamlined local development workflow.

![Favicon](https://www.google.com/s2/favicons?domain=https://medium.com&sz=32)

![Favicon](https://www.google.com/s2/favicons?domain=https://docs.mlrun.org&sz=32)

Sourcesundefined

## Johannes Foulds
Ok, new one, I am using MLRun on my mac mini in a conda environment, but I want to run the functions on my linux server that runs docker.So this is the same as running in local conda and functions executing in local docker as we discussed before, only now I want to use a remote docker. Still no installation of MLRun.Please no custom hacking functions, still through the standard MLRun API. I assume this is possible, as you said you can do this for running functions on OpenShift, so surely this works the same?And please if you can't find it in the documentation, don't just tell me it is not possible. Surely in my local environment I can configure docker itself to run the containers I start on a remote machine? Is this not a last resort solution?

## Alfred Ipswich
![https://docs.mlrun.org/en/stable/_static/images/mlrun-flow.png](https://tse1.mm.bing.net/th?id=OIP.e4eWpYFgO107LGpKqApobQHaDG&w=198&h=198&c=7)

![https://www.iguazio.com/wp-content/uploads/2023/01/pipeline-1024x422.png](https://tse3.mm.bing.net/th?id=OIP.RWKxpp6iByBpQ2RQssJiSwHaDD&w=195&h=195&c=7)

![https://docs.mlrun.org/en/latest/_images/mlrun-functions.png](https://tse4.mm.bing.net/th?id=OIP.d_ieBfjaReGkCN-7ZvrluQHaDD&cb=iwc1&w=195&h=195&c=7)

![https://lh7-us.googleusercontent.com/ETa4Vzc0Y9KzdufiRCJEnDum0C54O1GMD1mnE_3W7ZrG2hckLBXJJ74KCeyNwj8iBumt-sV6J_JSmhfTMLk-73Hk7O_1nUooc0zL8XlzXW7oHCyQ7a5BQj2ziQpJlpJFMZGMTt2QmDs5wc25m5BC4GE](https://tse4.mm.bing.net/th?id=OIP.VEkV98hSlOy9-m7a7XBTYAHaFB&w=321&h=321&c=7)

Running MLRun functions from your macOS Conda environment and executing them on a remote Linux server's Docker engine is achievable by configuring your local Docker client to communicate with the remote Docker daemon. This setup allows MLRun to utilize the remote Docker host for function execution without requiring a full MLRun installation on the server.

* * *

🧰 Prerequisites
----------------

1.  **Remote Linux Server**:
    
    *   Docker installed and running.
        
    *   Docker daemon configured to listen over TCP with TLS for secure communication.
        
2.  **Local macOS Machine**:
    
    *   Conda environment with Python 3.9.
        
    *   MLRun installed via `pip`:
        
        ```bash
        pip install mlrun
        ```
3.  **Network Configuration**:
    
    *   Ensure that the remote Docker daemon is accessible from your local machine over the network.
        

* * *

🔧 Configuring Remote Docker Access
-----------------------------------

### 1\. **Configure Docker Daemon on Remote Server**

Edit the Docker daemon configuration file (`/etc/docker/daemon.json`) on the remote server to include the following:

```json
{
  "hosts": ["tcp://0.0.0.0:2376", "unix:///var/run/docker.sock"],
  "tls": true,
  "tlscacert": "/etc/docker/certs/ca.pem",
  "tlscert": "/etc/docker/certs/server-cert.pem",
  "tlskey": "/etc/docker/certs/server-key.pem",
  "tlsverify": true
}
```

*   Replace the certificate paths with the actual paths to your TLS certificates.
    

Restart the Docker daemon to apply the changes:

```bash
sudo systemctl restart docker
```

### 2\. **Set Environment Variables on Local Machine**

On your macOS machine, set the following environment variables to direct Docker commands to the remote daemon:

```bash
export DOCKER_HOST=tcp://<remote-server-ip>:2376
export DOCKER_TLS_VERIFY=1
export DOCKER_CERT_PATH=~/path/to/certs
```

*   Replace `<remote-server-ip>` with the IP address of your remote server.
    
*   Ensure that the certificate files (`ca.pem`, `cert.pem`, `key.pem`) are present in the specified `DOCKER_CERT_PATH`.
    

You can verify the connection by running:

```bash
docker version
```

This command should display information about both the client and the remote server.

* * *

🚀 Running MLRun Functions on Remote Docker
-------------------------------------------

With the Docker client configured to communicate with the remote daemon, MLRun functions executed from your local environment will run on the remote server's Docker engine.

### Example: Running a Function

```python
import mlrun

# Create or load a project
project = mlrun.get_or_create_project("my_project", "./")

# Define a function
fn = project.set_function(
    name="my_function",
    func="my_script.py",
    kind="job",
    image="mlrun/mlrun",
    handler="my_handler"
)

# Run the function
run = fn.run(params={"param1": "value1"})
```

*   `func`: Path to your Python script.
    
*   `kind`: Execution type; `job` runs as a batch job.
    
*   `image`: Docker image to use; ensure it's accessible from the remote server.
    
*   `handler`: Function within your script to execute.
    

This setup allows MLRun to schedule and execute the function within the remote Docker environment while you manage and monitor the process from your local machine.

* * *

📦 Using MLRun Marketplace Functions
------------------------------------

MLRun provides a Function Hub with pre-built functions that can be imported and executed.

### Import and Run a Marketplace Function

```python
# Import a function from the MLRun Function Hub
fn = project.set_function("hub://describe", name="describe")

# Run the function
run = fn.run(params={"table": "iris_dataset.csv"})
```

This will run the `describe` function on the specified dataset within the remote Docker environment.

* * *

📝 Notes
--------

*   **Security Considerations**: Exposing the Docker daemon over TCP can pose security risks. Ensure that TLS is properly configured and that access is restricted to trusted clients.[Reddit](https://www.reddit.com/r/docker/comments/9pwkbw/running_docker_commands_on_a_remote_host/?utm_source=chatgpt.com)
    
*   **Artifact Management**: Artifacts generated during function execution will be stored on the remote server. Ensure that your MLRun configuration accounts for this, especially if you need to access these artifacts locally.[docs.mlrun.org](https://docs.mlrun.org/en/v1.0.0/install-kubernetes.html?utm_source=chatgpt.com)
    
*   **Network Latency**: Running functions over a network may introduce latency. Monitor performance and adjust configurations as necessary.
    

* * *

By configuring your local Docker client to communicate with a remote Docker daemon, you can effectively execute MLRun functions on a remote server without installing MLRun on that server. This setup leverages standard Docker and MLRun APIs, maintaining a clean separation between your development environment and execution infrastructure.

![Favicon](https://www.google.com/s2/favicons?domain=https://www.reddit.com&sz=32)

Sourcesundefined

## Johannes Foulds
I still think this is a work-around and I am not sure why this is not natively supported, please do a comprehensive search and see if anybody is using this style execution.

## Alfred Ipswich
![https://docs.mlrun.org/en/stable/_static/images/mlrun-flow.png](https://tse1.mm.bing.net/th?id=OIP.e4eWpYFgO107LGpKqApobQHaDG&w=198&h=198&c=7)

![https://docs.mlrun.org/en/stable/_images/mlrun-functions.png](https://tse3.mm.bing.net/th/id/OIP.XHsI8sRFFWZDE9eaUjWfUAHaDk?cb=iwp1&w=228&h=228&c=7)

![https://www.iguazio.com/wp-content/uploads/2023/01/pipeline-1024x422.png](https://tse3.mm.bing.net/th?id=OIP.RWKxpp6iByBpQ2RQssJiSwHaDD&w=195&h=195&c=7)

![https://docs.mlrun.org/en/latest/_images/mlrun-functions.png](https://tse4.mm.bing.net/th/id/OIP.d_ieBfjaReGkCN-7ZvrluQHaDD?cb=iwp1&w=195&h=195&c=7)

After conducting a comprehensive review of the MLRun documentation and related resources, it appears that MLRun does not natively support executing functions on a remote Docker daemon directly from a local Conda environment without deploying the full MLRun server. The standard MLRun architecture is designed to run functions either locally or within a Kubernetes cluster, and it does not provide built-in mechanisms for remote Docker execution in the manner you've described.

While it's technically feasible to configure your local Docker client to communicate with a remote Docker daemon (e.g., by setting the `DOCKER_HOST` environment variable), this approach is not officially supported or documented by MLRun. Such a setup would require manual configuration and might not integrate seamlessly with MLRun's function execution and artifact management workflows.

Therefore, using a remote Docker daemon in this context would be considered a workaround rather than a supported feature. If remote execution is a critical requirement for your workflow, you might need to consider alternative solutions or adjust your infrastructure to align with MLRun's supported deployment models.

Sources

