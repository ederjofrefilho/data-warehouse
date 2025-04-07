from airflow.decorators import dag
from airflow.models import Variable
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping
from pendulum import datetime
import os
import base64
import json

# Airbyte Connection
AIRBYTE_CONNECTION_ID = Variable.get("AIRBYTE META ADS -> POSTGRES")
AIRBYTE_ENDPOINT = "http://airbyte-server:8001/api/v1"

# dbt Settings
CONNECTION_ID = "postgres_conn"
DBT_PROJECT_PATH = f"{os.environ['AIRFLOW_HOME']}/dags/dbt/dbt_biera"
DBT_EXECUTABLE_PATH = f"{os.environ['AIRFLOW_HOME']}/dbt_venv/bin/dbt"

def airbyte_auth_header():
    username = "airbyte"
    password = "password"  # Substitua pela sua senha
    auth_str = f"{username}:{password}"
    auth_bytes = auth_str.encode("utf-8")
    base64_bytes = base64.b64encode(auth_bytes)
    return {"Authorization": f"Basic {base64_bytes.decode('utf-8')}"}

@dag(start_date=datetime(2025, 3, 26), schedule_interval="@daily", catchup=False)
def running_airbyte():

    # 1. Trigger Airbyte Sync (com tratamento correto da resposta)
    trigger_sync = HttpOperator(
        task_id="trigger_airbyte_sync",
        http_conn_id="airbyte",
        endpoint="/api/v1/connections/sync",
        method="POST",
        headers={
            **airbyte_auth_header(),
            "Content-Type": "application/json"
        },
        data=json.dumps({"connectionId": AIRBYTE_CONNECTION_ID}),
        response_check=lambda response: "job" in response.json(),
        response_filter=lambda response: response.json(),  # Armazena o JSON diretamente no XCom
        log_response=True
    )

    # 2. Sensor com template corrigido
    wait_for_sync = HttpSensor(
        task_id="wait_for_sync_completion",
        http_conn_id="airbyte",
        endpoint="/api/public/v1/jobs/{{ ti.xcom_pull(task_ids='trigger_airbyte_sync')['job']['id'] }}",  # Acesso direto ao dicionário
        method="GET",
        headers=airbyte_auth_header(),
        response_check=lambda response: response.json()["status"] == "succeeded",
        poke_interval=30,
        timeout=3600,
        mode="reschedule"
    )

    # 3. dbt Transformation
    transform_data = DbtTaskGroup(
        group_id="transform_data",
        project_config=ProjectConfig(DBT_PROJECT_PATH),
        profile_config=ProfileConfig(
            profile_name="default",
            target_name="dev",
            profile_mapping=PostgresUserPasswordProfileMapping(
                conn_id=CONNECTION_ID,
                profile_args={"schema": "staging"}
            )
        ),
        execution_config=ExecutionConfig(dbt_executable_path=DBT_EXECUTABLE_PATH)
    )

    trigger_sync >> wait_for_sync >> transform_data

running_airbyte_dag = running_airbyte()