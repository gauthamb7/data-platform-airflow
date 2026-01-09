"""
Customer 1 data pipeline.

This file only defines:
- Which tasks run
- In what order
"""

from datetime import datetime
from modules.dag_factory import CustomerDAGFactory
from modules.task_factory import PlatformTaskFactory


dag = CustomerDAGFactory.create(
    dag_id="customer1_pipeline",
    customer="customer1",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
)

tasks = PlatformTaskFactory(dag)

start = tasks.dummy_op("start")

validate = tasks.aks_op(
    task_id="validate",
    snapshot="s3://snapshots/customer1:v12",
    entrypoint="validate.py",
)

transform = tasks.aks_op(
    task_id="transform",
    snapshot="s3://snapshots/customer1:v12",
    entrypoint="transform.py",
)

def notify():
    print("Customer 1 pipeline completed")

notify_task = tasks.python_op("notify", notify)

upload = tasks.sftp_upload_op(
    task_id="upload_to_partner",
    local_path="/data/output.csv",
    remote_path="/incoming/customer1.csv",
    ssh_conn_id="partner_sftp",
)

end = tasks.dummy("end")

start >> validate >> transform >> notify_task >> upload >> end
