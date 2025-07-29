import os
from dotenv import load_dotenv
import psycopg2

def get_db_connection():
    """
    Creates and returns a database connection to PostgreSQL using environment variables
    """
    load_dotenv()  # Load environment variables
    
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT')
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None