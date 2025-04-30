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

### 🛠️ Como Adicionar Novos Pipelines

Este projeto integra Airbyte, Airflow e DBT para construção de pipelines de dados. Siga as etapas abaixo para adicionar um novo pipeline completo ao ecossistema:

---

#### 1. 🔌 Criar a Conexão no Airbyte

- Acesse a interface do **Airbyte**.
- Crie uma nova conexão entre a origem e o destino desejado.
- Após criada, copie o valor do campo `connectionId`.

---

#### 2. ⚙️ Criar a Variável no Airflow

- No **Airflow**, acesse o menu **Admin > Variables**.
- Crie uma nova variável com o seguinte formato de nome:

  ```
  AIRBYTE_CONNECTION_ID_<NOME_DO_PIPELINE>
  ```

- O valor da variável deve ser o `connectionId` copiado no passo anterior.
- Esta variável será usada pela DAG para orquestrar a sincronização dos dados.

---

#### 3. 📅 Criar a DAG no Airflow

- Crie uma nova DAG Python na pasta `dags/`.
- Utilize como modelo uma das DAGs existentes para manter o padrão do projeto.
- A DAG deve:
  - Buscar o `connectionId` via variável de ambiente.
  - Utilizar o `AirbyteTriggerSyncOperator` para iniciar a sincronização.
  - Monitorar o status com o `AirbyteJobSensor`.

---

#### 4. 🧪 Desenvolver os Models no DBT

- Crie os arquivos `.sql` correspondentes ao pipeline na pasta `dbt/models/`.
- Siga as boas práticas do DBT:
  - Use `stg_` para modelos de *staging*.
  - Use `fct_` ou `dim_` para modelos finais (*fato* ou *dimensão*).
- Atualize os arquivos `schema.yml` e `dbt_project.yml` se necessário.

---

#### 5. 🔁 Integrar Execução DBT na DAG

- Após a sincronização dos dados com o Airbyte, adicione tasks para executar os modelos DBT.
- Utilize os operadores:
  - `DBTRunOperator`: para executar os modelos.
  - `DBTTestOperator`: para rodar os testes.

- A ordem das tasks deve ser:
  1. `sync_airbyte`
  2. `run_dbt`
  3. `test_dbt`

---

📌 **Dica:**  

> **Nota:** A DAG `meta_ads_elt_pipeline.py` é usada apenas como exemplo.  
> Embora ela esteja configurada para o conector do **Meta Ads**, o projeto não é limitado a esse caso de uso.  
> Você pode usar esse exemplo como base para criar pipelines de qualquer origem e destino compatíveis com o Airbyte.  
> 
> As variáveis `AIRBYTE_META_ADS_POSTGRES_CONNECTION_ID` e `AIRBYTE_GS_CONNECTION_ID` são específicas do exemplo e **não são obrigatórias para o projeto como um todo**.  
> 
> No entanto, **as variáveis globais** abaixo **devem estar configuradas** no Airflow, pois são utilizadas para autenticação com a API do Airbyte:
>
> - `AIRBYTE_USERNAME`
> - `AIRBYTE_PASSWORD`


Você pode usar a DAG `meta_ads_elt_pipeline.py` (em `dags/`) como referência de estrutura.
