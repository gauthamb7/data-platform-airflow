"""
Platform task factory.

This file defines how tasks run (AKS, Python, SFTP, etc).
Customer DAGs only describe WHAT runs and in WHAT order.
"""

from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.sftp.operators.sftp import SFTPOperator


class PlatformTaskFactory:
    """Factory for creating platform-approved Airflow tasks."""

    def __init__(self, dag):
        self.dag = dag

    def aks_op(self, task_id, snapshot, entrypoint, cpu="2", memory="4Gi"):
        """
        Run Python code inside AKS using the platform runtime.

        Args:
            task_id (str)
            snapshot (str): Code or artifact location
            entrypoint (str): Python file to execute
        """
        return KubernetesPodOperator(
            dag=self.dag,
            task_id=task_id,
            name=task_id,
            namespace="data-pipelines",
            image="company/data-runtime:latest",
            cmds=["python", entrypoint],
            arguments=[snapshot],
            env_vars={"SNAPSHOT": snapshot},
            get_logs=True,
            is_delete_operator_pod=True,
            retries=3,
            resources={
                "request_cpu": cpu,
                "request_memory": memory,
                "limit_cpu": cpu,
                "limit_memory": memory,
            },
        )

    def python_op(self, task_id, python_callable, op_kwargs=None):
        """Run lightweight Python logic inside Airflow."""
        return PythonOperator(
            dag=self.dag,
            task_id=task_id,
            python_callable=python_callable,
            op_kwargs=op_kwargs or {},
        )

    def dummy_op(self, task_id):
        """Create a no-op task for flow control."""
        return EmptyOperator(dag=self.dag, task_id=task_id)

    def sftp_upload_op(self, task_id, local_path, remote_path, ssh_conn_id):
        """Upload a file to an SFTP server."""
        return SFTPOperator(
            dag=self.dag,
            task_id=task_id,
            ssh_conn_id=ssh_conn_id,
            local_filepath=local_path,
            remote_filepath=remote_path,
            operation="put",
        )
