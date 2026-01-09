# Airflow-based Data Execution Platform

This repository implements a multi-tenant, Kubernetes-native data execution platform on top of Apache Airflow.

It is designed to run hundreds of user pipelines using a single, stable DAG architecture where:
1. Users define what runs and in what order
2. The platform controls how it runs (AKS, retries, memory, secrets, images, logging)
3. This avoids DAG sprawl and enables safe, scalable data operations.

## Core Design Principles
| Principle         | Description                                          |
| ----------------- | ---------------------------------------------------- |
| Thin DAGs         | DAGs only define task order and dependencies         |
| Fat Platform      | Execution logic is centralized in factories          |
| Kubernetes Native | All heavy workloads run in AKS                       |
| Multi-Tenant      | One platform supports many users                 |
| CI/CD Friendly    | Business logic can be deployed independently of DAGs |

## Repository Structure
dags/
  user1_pipeline.py     # Customer-specific workflows

modules/
  dag_factory.py            # Platform DAG definition
  task_factory.py           # Platform execution runtime

## Architecture
User DAG
   │
   ▼
Platform DAG Factory   →  defines retries, SLAs, tags, governance
   │
   ▼
Platform Task Factory  →  defines how tasks run (AKS, Python, SFTP, etc)
   │
   ▼
AKS Runtime            →  executes user code snapshots

## DAG Factory

All Airflow policies live in one place:
- retries
- retry delay
- SLA
- tags
- ownership
Customer DAGs automatically inherit these.

dag = CustomerDAGFactory.create(...)

## Task Factory

The Task Factory exposes approved execution primitives:
| Method          | Purpose                  |
| --------------- | ------------------------ |
| `aks_python()`  | Run user code in AKS |
| `python()`      | Run lightweight Python   |
| `dummy()`       | Control flow             |
| `sftp_upload()` | Upload data to partners  |

## Example Customer DAG
tasks = PlatformTaskFactory(dag)

validate = tasks.aks_python("validate", snapshot, "validate.py")
transform = tasks.aks_python("transform", snapshot, "transform.py")
upload = tasks.sftp_upload("upload", "/data/out.csv", "/incoming/out.csv", "sftp")

validate >> transform >> upload

Users only describe:
- What tasks exist
- How they depend on each other
- They never manage:
- Kubernetes
- Docker
- Memory
- Retries
- Secrets

## Extension Possibilities

This platform can be extended to support:
1. Spark & Databricks: Run large-scale jobs on Spark clusters.
2. dbt & SQL Workloads: Add SQL model execution as first-class tasks.
3. Data Contracts: Validate schemas, nullability, and ranges before ingestion.
4. Observability: Emit OpenLineage, metrics, and per-user cost tracking.
5. YAML-Driven DAGs: Auto-generate DAGs from simple YAML files for 1000+ users.
6. Blue-Green Deployment: Run multiple snapshot versions side-by-side for safe rollouts.
