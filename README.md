# 📊 Data Warehouse Pipeline with Airbyte, Airflow, and dbt

This project implements an ELT pipeline using **Airbyte**, **Apache Airflow**, **Docker**, and **dbt**. It automates data extraction (e.g., Meta Ads), performs transformations with dbt, and manages orchestration via Airflow.

---

## 🚀 Technologies Used

- [Airbyte](https://airbyte.com/) (installed separately via `abctl`)  
- [Apache Airflow](https://airflow.apache.org/)  
- [Docker](https://www.docker.com/)  
- [Docker Compose](https://docs.docker.com/compose/)  
- [dbt (Data Build Tool)](https://www.getdbt.com/)  
- Python 3.12  

---

## 📁 Project Structure

```
data-warehouse-main/
├── dags/                       # Airflow DAGs
│   ├── meta_ads_elt_pipeline.py
│   └── dbt/
│       └── dbt_biera/          # dbt project
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── README.md
```

---

## ⚙️ How to Run the Project

1. **Clone the repository:**

```bash
git clone <REPOSITORY_URL>
cd data-warehouse-main
```

2. **Start the Airflow environment:**

```bash
docker-compose up --build
```

3. **Install and start Airbyte separately (via `abctl`):**

```bash
brew tap airbytehq/tap
brew install abctl
abctl local install
```

Access Airbyte at `http://localhost:8000` (or your configured port).

4. **Set up connections in Airbyte:**  
Create connections (e.g., Meta Ads → PostgreSQL) and copy each `connectionId`.

5. **In Airflow, go to `Admin > Variables` and add:**

- `AIRBYTE_META_ADS_POSTGRES_CONNECTION_ID`  
- `AIRBYTE_GS_CONNECTION_ID`  
- `AIRBYTE_USERNAME`  
- `AIRBYTE_PASSWORD`  

---

## 🧠 What the `meta_ads_elt_pipeline` DAG Does

- Triggers synchronization in Airbyte  
- Monitors execution status  
- Runs transformations with dbt-core  
- Orchestrates and monitors everything in the Airflow UI  

---

## ✅ Requirements

- Docker and Docker Compose  
- Airbyte installed separately via `abctl`  
- Connections and variables configured in Airflow  
- Data source integrated with Airbyte  
- Functional dbt project  

---

## 🛠️ How to Add New Pipelines

This project integrates Airbyte, Airflow, and dbt to build data pipelines. Follow the steps below to add a new full pipeline:

### 1. 🔌 Create the Connection in Airbyte

- Access the **Airbyte** interface  
- Create a new connection between the desired source and destination  
- Copy the `connectionId` value  

### 2. ⚙️ Create the Variable in Airflow

- In **Airflow**, go to **Admin > Variables**  
- Create a new variable with the following format:

```
AIRBYTE_CONNECTION_ID_<PIPELINE_NAME>
```

- Set the variable value as the copied `connectionId`  
- This variable will be used by the DAG to orchestrate synchronization  

### 3. 📅 Create the DAG in Airflow

- Create a new Python DAG in the `dags/` folder  
- Use an existing DAG as a template  
- The DAG should:  
  - Retrieve the `connectionId` via environment variable  
  - Use `AirbyteTriggerSyncOperator` to start synchronization  
  - Monitor status with `AirbyteJobSensor`  

### 4. 🧪 Develop the Models in dbt

- Create `.sql` files for the pipeline in `dbt/models/`  
- Follow dbt best practices:  
  - `stg_` for staging models  
  - `fct_` or `dim_` for final models (fact/dimension)  
- Update `schema.yml` and `dbt_project.yml` if necessary  

### 5. 🔁 Integrate dbt Execution in the DAG

- After Airbyte synchronization, add tasks to run dbt models  
- Use operators:  
  - `DBTRunOperator` to execute models  
  - `DBTTestOperator` to run tests  

- Task order:  
  1. `sync_airbyte`  
  2. `run_dbt`  
  3. `test_dbt`  

---

📌 **Tip:**  

> **Note:** The DAG `meta_ads_elt_pipeline.py` is an example.  
> It is configured for the **Meta Ads** connector but the project is not limited to this use case.  
> You can use it as a base to create pipelines for any Airbyte-compatible source and destination.  
>
> The variables `AIRBYTE_META_ADS_POSTGRES_CONNECTION_ID` and `AIRBYTE_GS_CONNECTION_ID` are example-specific and **not required for the entire project**.  
>
> However, the global variables below **must be configured** in Airflow for Airbyte API authentication:  
> - `AIRBYTE_USERNAME`  
> - `AIRBYTE_PASSWORD`  

You can use `meta_ads_elt_pipeline.py` (in `dags/`) as a reference for structure.
