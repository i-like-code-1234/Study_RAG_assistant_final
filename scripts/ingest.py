from langchain_community.document_loaders import PyPDFLoader
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from db_connection import get_db_connection
import json
from openai import OpenAI
from dotenv import load_dotenv  


data_path = "/workspaces/Study_RAG_assistant/data/"
load_dotenv()
client=OpenAI(api_key = os.getenv("OPENAI_API_KEY"))


def get_embedding(string):
 response = client.embeddings.create(
         model="text-embedding-ada-002",
         input=string
     )
 return response




def load_docs_and_chunk(folder_path):
    """
    Loads all PDF files from a folder into documents and chunks them
    """
    page_documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            page_documents.extend(documents)
    text_splitter = RecursiveCharacterTextSplitter(
       chunk_size=1000,
       chunk_overlap=500,
       length_function=len,
       add_start_index=True
    )
    chunked_documents = text_splitter.split_documents(page_documents)
    return chunked_documents



def init_db_table(conn, cursor):
    """
    Creates the table for storing document embeddings if it doesn't exist
    """
    try:
        # Enable pgvector extension
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")  
        # Create table with vector column
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                content TEXT,
                metadata JSONB,
                embedding vector(1536)
                
            )
        """)
        conn.commit()
        print("Database table initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()


# Add this to your main ingest() function:
def ingest():
    """
    Main function orchestrating the pipeline
    """
    chunked_documents=load_docs_and_chunk(data_path)
    conn = get_db_connection()
    cursor = conn.cursor()
    init_db_table(conn, cursor)

    for doc in chunked_documents:
     
        content = doc.page_content.replace('\x00', '') # get rid of null characters
        metadata = json.dumps(doc.metadata)
        embedding = get_embedding(content).data[0].embedding  # get embedding for the content
        #get embedding for the content
        cursor.execute("INSERT INTO documents (content, metadata,embedding) VALUES (%s, %s,%s) ", (content, metadata,embedding))
       
    conn.commit()   
    cursor.close()     
    conn.close() 



    
    






#RUN THIS 
#if __name__ == "__main__":
    #this if statement just means "if this file is run directly, execute the ingest function"
   # ingest()



def fetch_nth_row(n):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, content, metadata, embedding
          FROM documents
          ORDER BY id 
          LIMIT 1
          OFFSET %s
    """, (n-1,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row
    
#print(fetch_nth_row(1))  # Example usage, fetches the first row
"""
conn = get_db_connection()
cur = conn.cursor()
with conn.cursor() as cur:
    cur.execute("DELETE FROM documents;")
    cur.execute("ALTER SEQUENCE documents_id_seq RESTART WITH 1;")
    conn.commit()
cur.close()
conn.close()
"""
