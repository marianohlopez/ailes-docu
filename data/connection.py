import os
import mysql.connector
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()   

# def get_connection():
#     return mysql.connector.connect(
#         host=os.getenv("DB_HOST"),
#         port=os.getenv("DB_PORT"),
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASS"),
#         database=os.getenv("DB_NAME"),
#     )

def get_connection():
    # Construir la URL de conexión para SQLAlchemy + PyMySQL
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    dbname = os.getenv("DB_NAME")

    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
    engine = create_engine(connection_string, pool_pre_ping=True)  # pool_pre_ping para validar conexiones

    return engine