import yfinance as yf
import json
import time
from datetime import datetime
from google.cloud import pubsub_v1
from dotenv import load_dotenv
import os

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
PROJECT_ID   = os.getenv("GCP_PROJECT_ID")
TOPIC_ID     = os.getenv("PUBSUB_TOPIC_ID")
KEY_PATH     = os.getenv("GCP_KEY_PATH")
TICKERS      = ["AAPL", "GOOGL", "MSFT", "AMZN", "META"]
INTERVAL_SEC = 60  # Publier toutes les 60 secondes

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

# ── Client Pub/Sub ────────────────────────────────────────────────────────────
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

def fetch_stock_data(ticker: str) -> dict:
    """
    Récupère le dernier prix disponible pour un ticker.
    .history(period='1d', interval='1m') = données de la journée minute par minute.
    On prend la dernière ligne = le prix le plus récent.
    """
    df = yf.Ticker(ticker).history(period="1d", interval="1m")
    if df.empty:
        return None
    last = df.iloc[-1]  # Dernière ligne = donnée la plus récente
    return {
        "ticker":       ticker,
        "timestamp":    datetime.utcnow().isoformat(),
        "open":         round(float(last["Open"]),   4),
        "high":         round(float(last["High"]),   4),
        "low":          round(float(last["Low"]),    4),
        "close":        round(float(last["Close"]),  4),
        "volume":       int(last["Volume"]),
        "daily_return": round(float(
            (last["Close"] - last["Open"]) / last["Open"] * 100
        ), 4),
    }

def publish_message(data: dict):
    """
    Publie un message JSON dans Pub/Sub.
    Pub/Sub n'accepte que des bytes → on encode en UTF-8.
    future.result() attend la confirmation de réception par GCP.
    """
    message_bytes = json.dumps(data).encode("utf-8")
    future = publisher.publish(topic_path, message_bytes)
    future.result()  # Attendre confirmation
    print(f"✅ Publié : {data['ticker']} | close={data['close']} | {data['timestamp']}")

def run():
    print(f"🚀 Publisher démarré — envoi toutes les {INTERVAL_SEC}s")
    print(f"   Topic : {topic_path}")
    print(f"   Tickers : {TICKERS}\n")

    while True:
        for ticker in TICKERS:
            data = fetch_stock_data(ticker)
            if data:
                publish_message(data)
            else:
                print(f"⚠️  Pas de données pour {ticker} (marché fermé ?)")

        print(f"\n⏳ Attente {INTERVAL_SEC} secondes...\n")
        time.sleep(INTERVAL_SEC)

if __name__ == "__main__":
    run()