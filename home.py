import streamlit as st
import requests
import os
from collections import defaultdict



def format_response(response):
   chatgpt_response, poor_search_warning, list_of_references, list_of_context_strings = (
        response["chatgpt_response"],
        response["poor_search_warning"],
        response["list_of_references"],
        response["list_of_context_strings"],
    )


   # Main Answer
   st.markdown("### 💬 ChatGPT's Answer")
   st.markdown(chatgpt_response)

   # Warning about poor search quality
   if poor_search_warning:
        st.warning("⚠️ The retrieved documents had low similarity. The answer may be less reliable.")
    

   # References used
   st.markdown("### 📄 Sources Used")
   #put sources in nice dictionary like format
   
   grouped_refs = defaultdict(list)
   for filename, page in list_of_references:
    if page not in grouped_refs[filename]:
        grouped_refs[filename].append(page)


   #display sources nicely
   for filename, pages in grouped_refs.items():
    page_list = ", ".join(str(p+1) for p in sorted(pages))
    st.markdown(f"**{filename}** — Pages: {page_list}")
  

   

   # Optional: Show raw context strings from similarity search 
   with st.expander("🔎 Show retrieved context passages"):
        for i, context in enumerate(list_of_context_strings, 1):
            st.markdown(f"**Passage {i}:**")
            st.markdown(f"> {context}")
            st.markdown(f" > **Taken from `{list_of_references[i-1][0]}` : Page {list_of_references[i-1][1] + 1}**")
            st.markdown("---")


   

#MAKE A SIMPLE INTRO 
data_path = "/workspaces/Study_RAG_assistant/data/"
list_of_files=[]
for filename in os.listdir(data_path):
 if filename.endswith('.pdf'):
  list_of_files.append(filename)
st.set_page_config(page_title="Study RAG Assistant", page_icon="📚", layout="wide")
st.title("📚 Study RAG Assistant")
st.caption("Ask questions about your PDFs. I'll search through your listed documents and create a response!")
st.markdown(
    """
**How it works**
1. Select PDFs you want to search through
2. Ask a question
3. Get an answer with references and information about the response.
    """
)
st.divider()


# Push down with blank lines 
for _ in range(2):
    st.write("")



#make columns for user input
col1, col2, col3 = st.columns([4, 3, 1], gap="small")
with col1:
    user_query = st.text_input("", placeholder="Enter your question here")  #THIS IS DODGY, could cause issues

with col2:
    file_selections = st.multiselect("Select files", list_of_files)

with col3:
    st.write("")
    st.write("")
    send = st.button("Send")



# Send both pieces of data off to the API
if send:
    if not user_query:
        st.warning("Please enter a query before submitting.")
    elif not file_selections:
        st.warning("Please select at least one file.")
    else:
        user_query_and_file_selection = {"query": user_query, "files": file_selections}
        response = requests.post("http://127.0.0.1:8000/query", json=user_query_and_file_selection)
        if response.status_code == 200:
           format_response(response.json())   #THIS IS ME CALLING THE RESPONSE
        else:
            st.error(f"API returned status code {response.status_code}")


