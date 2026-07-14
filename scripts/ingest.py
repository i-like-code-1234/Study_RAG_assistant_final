from langchain_community.document_loaders import PyPDFLoader
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from db_connection import get_db_connection
import json
from openai import OpenAI
from dotenv import load_dotenv  


data_path = "/workspaces/Study_RAG_assistant_final/data/"
load_dotenv()
client=OpenAI(api_key = os.getenv("OPENAI_API_KEY"))


def get_embedding(string):
 response = client.embeddings.create(
         model="text-embedding-ada-002",
         input=string
     )
 return response


def load_docs_and_chunk(folder_path, chunk_size, overlap):
    chunks = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Build a list of (word, page_number) tuples
            word_page_pairs = []
            for page in documents:
                page_number = page.metadata["page"]
                for word in page.page_content.split():
                    word_page_pairs.append((word, page_number))
            
            # Chunk using word_page_pairs
            i = 0
            while i < len(word_page_pairs):
                start = max(0, i - overlap)
                end = min(len(word_page_pairs), i + overlap)
                chunk_pairs = word_page_pairs[start:end]
                chunk_text = " ".join([pair[0] for pair in chunk_pairs])
                # Get the page number from the middle of the chunk
                middle_page = word_page_pairs[i][1]
                chunks.append({
                    "content": chunk_text,
                    "metadata": {"source": file_path, "page": middle_page}
                })
                i += chunk_size
    
    return chunks


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


def ingest():
    """
    Main function orchestrating the pipeline
    """
    chunked_documents=load_docs_and_chunk(data_path,200,180)
    conn = get_db_connection()
    cursor = conn.cursor()
    init_db_table(conn, cursor)

    for doc in chunked_documents:
     
        content = doc["content"].replace('\x00', '')
        metadata = json.dumps(doc["metadata"])
        embedding = get_embedding(content).data[0].embedding  # get embedding for the content
        #get embedding for the content
        cursor.execute("INSERT INTO documents (content, metadata,embedding) VALUES (%s, %s,%s) ", (content, metadata,embedding))
       
    conn.commit()   
    cursor.close()     
    conn.close() 


#RUN THIS 
if __name__ == "__main__":
    #this if statement just means "if this file is run directly, execute the ingest function"
   ingest()

