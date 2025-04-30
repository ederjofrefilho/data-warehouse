
# 📊 Data Warehouse Pipeline com Airbyte, Airflow e dbt

Este projeto implementa um pipeline ELT utilizando **Airbyte**, **Apache Airflow**, **Docker** e **dbt**. Ele automatiza a extração de dados (ex: Meta Ads), realiza transformações com dbt e gerencia toda a orquestração via Airflow.

---

## 🚀 Tecnologias Utilizadas

- [Airbyte](https://airbyte.com/) (instalado separadamente via `abctl`)
- [Apache Airflow](https://airflow.apache.org/)
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [dbt (Data Build Tool)](https://www.getdbt.com/)
- Python 3.12

---

## 📁 Estrutura do Projeto

```
data-warehouse-main/
├── dags/                       # DAGs do Airflow
│   ├── meta_ads_elt_pipeline.py
│   └── dbt/
│       └── dbt_biera/          # Projeto dbt
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── README.md
```

---

## ⚙️ Como Rodar o Projeto

1. **Clone o repositório**:

```bash
git clone <URL_DO_REPOSITORIO>
cd data-warehouse-main
```

2. **Suba o ambiente do Airflow**:

```bash
docker-compose up --build
```

3. **Instale e inicie o Airbyte separadamente (via `abctl`)**:

```bash
brew tap airbytehq/tap
brew install abctl
abctl local install
```

Acesse o Airbyte em `http://localhost:8000` (ou a porta que você definiu).

4. **Configure as conexões no Airbyte**:

Crie as conexões (por exemplo, Meta Ads → PostgreSQL) e copie o `connectionId` de cada uma.

5. **No Airflow, acesse `Admin > Variables` e adicione**:

- `AIRBYTE_META_ADS_POSTGRES_CONNECTION_ID`
- `AIRBYTE_GS_CONNECTION_ID`
- `AIRBYTE_USERNAME`
- `AIRBYTE_PASSWORD`

---

## 🧠 O que o DAG `meta_ads_elt_pipeline` faz?

- Aciona sincronização no Airbyte
- Monitora status da execução
- Executa transformações com dbt-core
- Orquestra e monitora tudo na interface do Airflow

---

## ✅ Requisitos

- Docker e Docker Compose
- Airbyte instalado separadamente com `abctl`
- Conexões e variáveis configuradas no Airflow
- Fonte de dados integrada ao Airbyte
- Projeto dbt funcional
