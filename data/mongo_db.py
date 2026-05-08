from pymongo import MongoClient
from datetime import datetime
import os

uri = os.environ.get("MONGO_URL") 
mongo_db = os.environ.get("MONGO_DB") 

def get_mongo_client():
  client = MongoClient(uri)
  return client

def register(st):
  try:
    client = get_mongo_client()
    db = client[mongo_db]
    col = db["tableros_logs"]

    today = datetime.now().date()

    exists = col.find_one({
      "$expr": {
        "$eq": [{"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}, str(today)]
      },
      "tablero": "Documentacion"
    })

    if not exists:
      col.insert_one({
        "timestamp": datetime.now(),
        "tablero": "Documentacion"
      })

    client.close()
  except Exception as e:
    st.error(f"Error MongoDB: {e}")

