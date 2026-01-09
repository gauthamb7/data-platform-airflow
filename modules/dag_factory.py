"""
Centralized DAG factory.

All platform-level defaults (retries, alerts, tags, SLAs, etc.)
are controlled here so customer DAGs stay clean and consistent.
"""

from airflow import DAG
from datetime import timedelta


class CustomerDAGFactory:
    """Factory to create standardized customer DAGs."""

    DEFAULT_ARGS = {
        "owner": "data-platform",
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": False,
        "email_on_retry": False,
    }

    @classmethod
    def create(cls, dag_id, customer, start_date, schedule):
        """
        Create a customer DAG with platform defaults applied.

        Args:
            dag_id (str): Airflow DAG name
            customer (str): Customer identifier
            start_date (datetime): DAG start date
            schedule (str): Cron or preset schedule

        Returns:
            airflow.DAG
        """
        return DAG(
            dag_id=dag_id,
            start_date=start_date,
            schedule_interval=schedule,
            catchup=False,
            default_args=cls.DEFAULT_ARGS,
            tags=["data-platform", customer],
        )
