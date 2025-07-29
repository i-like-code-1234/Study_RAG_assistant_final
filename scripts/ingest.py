from langchain_community.document_loaders import PyPDFLoader
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from db_connection import get_db_connection



def preprocess_documents():
    """
    Cleans and splits documents into chunks
    Returns list of processed chunks with metadata
    """
    pass
def create_embeddings():
    """
    Creates embeddings from text chunks
    Returns vectors ready for database insertion
    """
    pass
def store_vectors(conn, cursor):
    """
    Stores vectors in pgvector database
    Handles insertions and transaction management. no need to use batch insertsion - most simple way
    """
    pass

def ingest():
    """
    Main function. Orchestrates the pipeline with proper DB connection handling:
    connect -> load -> process -> embed -> store -> close connection when done
    """
    pass
if __name__ == "__main__":
    ingest()





data_path = "/workspaces/Study_RAG_assistant/data/"

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


chunked_documents=load_docs_and_chunk(data_path)






















"""
from langchain.document_loaders import DirectoryLoader 
data_path="data/books" 
def load_documents():
     loader=DirectoryLoader(data_path,glob="*.md") 
     documents=loader.load()
     return documents



text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=500,length_function=len,add_start_index=True)
chunks=text_splitter.split_documents(documents)


 
"""

