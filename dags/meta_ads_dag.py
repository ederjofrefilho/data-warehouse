"""
### DAG de Pipeline ELT com Airbyte e dbt

Este DAG automatiza o processo de:
1. Acionar sincronização de dados do Meta Ads via Airbyte
2. Monitorar conclusão da sincronização
3. Executar transformações de dados com dbt

**Recursos:**
- Autenticação segura no Airbyte via variáveis
- Tratamento robusto de erros
- Monitoramento detalhado na UI
- Configuração centralizada
- Documentação integrada
"""

from datetime import datetime
import os
import base64
import json

from airflow.decorators import dag, task_group
from airflow.models import Variable
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping
from pendulum import datetime as pendulum_datetime

# Region: Configurações Globais
AIRBYTE_CONNECTION_ID = Variable.get("AIRBYTE_META_ADS_POSTGRES_CONNECTION_ID")
AIRBYTE_USERNAME = Variable.get("AIRBYTE_USERNAME", default_var="airbyte")
AIRBYTE_PASSWORD = Variable.get("AIRBYTE_PASSWORD")

DBT_CONFIG = {
    "project_path": f"{os.environ['AIRFLOW_HOME']}/dags/dbt/dbt_biera",
    "executable_path": f"{os.environ['AIRFLOW_HOME']}/dbt_venv/bin/dbt",
    "connection_id": "postgres_conn",
    "target_schema": "staging",
    "target_env": "dev"
}

DEFAULT_ARGS = {
    "owner": "admin",
    "retries": 2,
    "retry_delay": 30,
    "start_date": pendulum_datetime(2024, 3, 1),
    "depends_on_past": False
}
# EndRegion

def generate_airbyte_auth() -> dict:
    """
    Gera header de autenticação para o Airbyte
    Returns:
        dict: Header de autenticação Basic Auth
    """
    auth_str = f"{AIRBYTE_USERNAME}:{AIRBYTE_PASSWORD}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    return {"Authorization": f"Basic {auth_b64}"}

@dag(
    schedule_interval="@daily",
    start_date=DEFAULT_ARGS["start_date"],
    catchup=False,
    default_args=DEFAULT_ARGS,
    max_active_runs=1,
    tags=["elt", "airbyte", "dbt", "meta_ads"]
)
def meta_ads_elt_pipeline():

    @task_group(group_id="airbyte_sync")
    def airbyte_sync_group():
        """Grupo de tarefas para execução da sincronização Airbyte"""
        
        # Tarefa para iniciar a sincronização
        trigger_sync = HttpOperator(
            task_id="trigger_connection_sync",
            http_conn_id="airbyte",
            endpoint="/api/v1/connections/sync",
            method="POST",
            headers={
                **generate_airbyte_auth(),
                "Content-Type": "application/json"
            },
            data=json.dumps({"connectionId": AIRBYTE_CONNECTION_ID}),
            response_check=lambda response: (
                response.json().get("job", {}).get("status") == "running"
            ),
            response_filter=lambda response: response.json(),
            log_response=True
        )

        # Sensor para monitorar conclusão
        sync_monitor = HttpSensor(
            task_id="monitor_sync_status",
            http_conn_id="airbyte",
            endpoint=(
                "/api/public/v1/jobs/" 
                "{{ ti.xcom_pull(task_ids='airbyte_sync.trigger_connection_sync', key='return_value')['job']['id'] }}"
            ),
            method="GET",
            headers=generate_airbyte_auth(),
            response_check=lambda response: response.json()["status"] == "succeeded",
            poke_interval=60,
            timeout=3600,
            mode="reschedule"
        )

        trigger_sync >> sync_monitor

    @task_group(group_id="dbt_processing")
    def dbt_transform_group():
        """Grupo de tarefas para transformações dbt"""
        
        return DbtTaskGroup(
            group_id="data_transformations",
            project_config=ProjectConfig(DBT_CONFIG["project_path"]),
            profile_config=ProfileConfig(
                profile_name="default",
                target_name=DBT_CONFIG["target_env"],
                profile_mapping=PostgresUserPasswordProfileMapping(
                    conn_id=DBT_CONFIG["connection_id"],
                    profile_args={"schema": DBT_CONFIG["target_schema"]}
                )
            ),
            execution_config=ExecutionConfig(
                dbt_executable_path=DBT_CONFIG["executable_path"],
            ),
            operator_args={
                "install_deps": True,
                "full_refresh": True
            }
        )

    # Orquestração do pipeline
    airbyte_sync_group() >> dbt_transform_group()

meta_ads_elt_dag = meta_ads_elt_pipeline()