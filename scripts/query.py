
from db_connection import get_db_connection
from ingest import get_embedding
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from collections import defaultdict
import os


CHATGPT_PROMPT_TEMPLATE = """
Answer the question based on the following context
-- It is important you answer each question fully and specifically
-- Remember you are a teacher, be kind and helpfull
{context}

---

Answer the question based on the above context: {question}
"""



#function accepts two arguments: a python string (our user query), and a python list of strings (list of files we want to search through to answer query)
#this then returns the original query string, and a list of tuples, each tuple containing the id, content, metadata, and embedding of the documents that match the query
def perform_similarity_search(query_string, file_selections,number_of_results=4):
 
 query_string_embedding=get_embedding(query_string) 
 directory_string   = '/workspaces/Study_RAG_assistant_final/data'   #edit file_selections
 file_selections=[f"{directory_string}/{file_name}" for file_name in file_selections]

 conn = get_db_connection()
 cur = conn.cursor()

 sql = """
            SELECT
              id,
              content,
              metadata,
              embedding <=> %s::vector AS similarity
            FROM documents
            WHERE metadata->>'source' = ANY(%s)
            ORDER BY similarity ASC
            LIMIT %s;
            """
 params = (
            query_string_embedding.data[0].embedding,  # embedding for the query string
            file_selections,  # selection of file paths to look through
            number_of_results
            )
 
 cur.execute(sql, params)
 results = cur.fetchall()
 cur.close()
 conn.close()
 return query_string_embedding, results


#result_=perform_similarity_search("What does it mean to be human?", ['Analysis.pdf','chp1_.pdf'],number_of_results=3)[1]


def get_chatgpt_response(search_result,user_query):    
    #here we create chatgpt prompt
    context_string = "\n\n---\n\n".join([result[1] for result in search_result])
    prompt_template = ChatPromptTemplate.from_template(CHATGPT_PROMPT_TEMPLATE)
    chatgpt_prompt = prompt_template.format(context=context_string, question=user_query)
    model = ChatOpenAI()              # defaults to gpt-3.5-turbo
    chatgpt_response = model.invoke(chatgpt_prompt)
    return chatgpt_response.content





def make_list_of_references(results):      # DO THIS WITH LIST COMPRAHENSION
   list_of_references=[]
   for result in results:
      base_file=os.path.basename(result[2]['source'])
      page_no=result[2]['page']
      list_of_references.append([base_file,page_no])
   return list_of_references




def main_pipeline(user_query,file_selections):
    results_from_datatable_search=perform_similarity_search(user_query, file_selections,number_of_results=5)[1]
    chatgpt_response=get_chatgpt_response(results_from_datatable_search,user_query) #type string -- actuall response from chatgpt as a string
    poor_search_warning = any(result[3] > 0.2 for result in results_from_datatable_search) #type boolean--returns false if the similarity search results are good (cosine similarity is low), true if they are poor
    list_of_references=make_list_of_references(results_from_datatable_search) # returns list, each element in list is of the form ['some_file_name.pdf',some_page_number], each element is the reference information of the strings returned from the similarity search
    list_of_context_strings=[result[1] for result in results_from_datatable_search] #type string--list of the strings chatgpt used to answer the user_query i.e list of strings got from the similarity search
    return  chatgpt_response, poor_search_warning,list_of_references, list_of_context_strings


