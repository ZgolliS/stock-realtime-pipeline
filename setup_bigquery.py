from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GCP_KEY_PATH")

client = bigquery.Client()

# Créer le dataset
dataset_id = f"{os.getenv('GCP_PROJECT_ID')}.{os.getenv('BQ_DATASET')}"
dataset = bigquery.Dataset(dataset_id)
dataset.location = "EU"
client.create_dataset(dataset, exists_ok=True)
print(f"Dataset créé : {dataset_id}")

# Créer la table avec le schema
schema = [
    bigquery.SchemaField("ticker",       "STRING"),
    bigquery.SchemaField("timestamp",    "STRING"),
    bigquery.SchemaField("open",         "FLOAT"),
    bigquery.SchemaField("high",         "FLOAT"),
    bigquery.SchemaField("low",          "FLOAT"),
    bigquery.SchemaField("close",        "FLOAT"),
    bigquery.SchemaField("volume",       "INTEGER"),
    bigquery.SchemaField("daily_return", "FLOAT"),
]

table_ref = f"{dataset_id}.{os.getenv('BQ_TABLE')}"
table = bigquery.Table(table_ref, schema=schema)
client.create_table(table, exists_ok=True)
print(f"Table créée : {table_ref}")