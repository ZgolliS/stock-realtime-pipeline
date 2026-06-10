from google.cloud import pubsub_v1, bigquery
from dotenv import load_dotenv
import os, json, time

load_dotenv()

PROJECT_ID       = os.getenv("GCP_PROJECT_ID")
SUBSCRIPTION_ID  = os.getenv("PUBSUB_SUBSCRIPTION_ID")
BQ_DATASET       = os.getenv("BQ_DATASET")
BQ_TABLE         = os.getenv("BQ_TABLE")
KEY_PATH         = os.getenv("GCP_KEY_PATH")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

subscriber  = pubsub_v1.SubscriberClient()
bq_client   = bigquery.Client()
sub_path    = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)
table_ref   = f"{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"

def callback(message):
    """
    Callback appelé automatiquement à chaque message reçu.
    Pub/Sub appelle cette fonction dès qu'un message arrive dans le topic.
    message.ack() confirme la réception — Pub/Sub supprime alors le message.
    Sans ack(), Pub/Sub renverrait le message indéfiniment.
    """
    try:
        data = json.loads(message.data.decode("utf-8"))
        print(f"📥 Reçu : {data['ticker']} | close={data['close']} | {data['timestamp']}")

        # Insérer dans BigQuery
        errors = bq_client.insert_rows_json(table_ref, [data])
        if errors:
            print(f"❌ Erreur BigQuery : {errors}")
        else:
            print(f"✅ Inséré dans BigQuery : {data['ticker']}")

        message.ack()  # Confirmer réception à Pub/Sub

    except Exception as e:
        print(f"❌ Erreur : {e}")
        message.nack()  # Rejeter le message → Pub/Sub le renvoie

def run():
    print(f"🚀 Subscriber démarré")
    print(f"   Subscription : {sub_path}")
    print(f"   BigQuery table : {table_ref}\n")

    streaming_pull = subscriber.subscribe(sub_path, callback=callback)
    print("⏳ En attente de messages Pub/Sub...\n")

    try:
        streaming_pull.result()  # Écoute en continu indéfiniment
    except KeyboardInterrupt:
        streaming_pull.cancel()
        print("\n🛑 Subscriber arrêté")

if __name__ == "__main__":
    run()