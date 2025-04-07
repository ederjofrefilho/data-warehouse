from airflow.decorators import dag
from airflow.models import Variable
from airflow.providers.http.operators.http import HttpOperator
from airflow.operators.python import PythonOperator
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping
from pendulum import datetime
from datetime import datetime
import os
import base64
import json

## Airbyte Connection
AIRBYTE_CONNECTION_ID = Variable.get("AIRBYTE META ADS -> POSTGRES")

## dbt-core Settings
YOUR_NAME = "admin"
CONNECTION_ID = "postgres_conn" # Airflow databse connection
DB_NAME = "warehouse"
SCHEMA_NAME = "staging"
MODEL_TO_QUERY = "meta_ads_campaigns" # Script to execute that can be founded at dbt/models/...
DBT_PROJECT_PATH = f"{os.environ['AIRFLOW_HOME']}/dags/dbt/dbt_biera" # The path to the dbt project
DBT_EXECUTABLE_PATH = f"{os.environ['AIRFLOW_HOME']}/dbt_venv/bin/dbt" # The path where Cosmos will find the dbt executable in the virtual environment created in the Dockerfile

profile_config = ProfileConfig(
    profile_name="default",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id=CONNECTION_ID,
        profile_args={"schema": SCHEMA_NAME},
    ),
)

execution_config = ExecutionConfig(
    dbt_executable_path=DBT_EXECUTABLE_PATH,
)

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

    transform_data = DbtTaskGroup(
        group_id="transform_data",
        project_config=ProjectConfig(DBT_PROJECT_PATH),
        profile_config=profile_config,
        execution_config=execution_config,
        default_args={"retries": 2},
    )

    trigger_sync >> transform_data

running_airbyte()