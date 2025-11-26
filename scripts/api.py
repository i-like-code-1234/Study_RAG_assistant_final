from fastapi import FastAPI, Request

from query import main_pipeline

app = FastAPI()

@app.post("/query")
async def handle_query(request: Request):
    data = await request.json()
    
    user_query = data.get("query", []) #as string
    file_selections = data.get("files", [])  #as string
    query_response = main_pipeline(user_query, file_selections)

    return {
        "chatgpt_response": query_response[0],                    # chatgpt response as string
        "poor_search_warning": query_response[1],                 # boolean indicating if the search was poor
        "list_of_references": query_response[2],                  #information about the references used by chatgpt as list of lists
        "list_of_context_strings": query_response[3]              # context strings used by chatgpt as list of strings
           }
     
    
  
    
    
   


