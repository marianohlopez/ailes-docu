import os
import mysql.connector
import streamlit as st
from dotenv import load_dotenv

load_dotenv()   

# mantiene el objeto vivo mientras la app corre
@st.cache_resource(show_spinner=False)

def get_connection_creator():
    def connect():
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
        )
    return connect