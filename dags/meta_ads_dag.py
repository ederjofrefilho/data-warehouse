from airflow.decorators import dag
from airflow.models import Variable
from datetime import datetime
from airflow.providers.http.operators.http import HttpOperator
from airflow.operators.python import PythonOperator
import base64
import json

# Variáveis armazenadas no Airflow
AIRBYTE_CONNECTION_ID = Variable.get("AIRBYTE META ADS -> POSTGRES")

@dag(start_date=datetime(2025, 3, 26), schedule_interval="@daily", catchup=False)
def running_airbyte():

    def build_basic_auth_header(username, password):
        auth_str = f"{username}:{password}"
        auth_bytes = auth_str.encode("utf-8")
        base64_bytes = base64.b64encode(auth_bytes)
        return f"Basic {base64_bytes.decode('utf-8')}"

    def trigger_airbyte_sync(**context):
        from airflow.providers.http.operators.http import HttpOperator

        basic_auth_header = build_basic_auth_header("airbyte", "password")

        sync_operator = HttpOperator(
            task_id="trigger_airbyte_sync",
            http_conn_id="airbyte", 
            endpoint="/api/v1/connections/sync",
            method="POST",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": basic_auth_header
            },
            data=json.dumps({
                "connectionId": AIRBYTE_CONNECTION_ID
            }),
            log_response=True
        )
        return sync_operator.execute(context=context)

    trigger_sync = PythonOperator(
        task_id="run_sync",
        python_callable=trigger_airbyte_sync,
        provide_context=True,
    )

    trigger_sync

running_airbyte()
