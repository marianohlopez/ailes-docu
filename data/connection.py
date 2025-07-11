import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()   

def get_connection():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    dbname = os.getenv("DB_NAME")

    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
    engine = create_engine(connection_string, pool_pre_ping=True)

    return engine