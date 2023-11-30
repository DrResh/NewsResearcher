import os
import streamlit as st
import pickle
import time
from langchain.llms import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from ApiKey import openapi_key

import os
os.environ['OPENAI_API_KEY'] = openapi_key



st.title("News Researcher")
st.sidebar.title("News URLs")
urls = []
for i in range(3):
    url = st.sidebar.text_input(f"URL {i+1}")
    urls.append(url)

analyse_btn = st.sidebar.button("Analyse")
file_path = "faiss_store.pkl"

main_placeholder = st.empty()

llm = OpenAI(temperature=0.9, max_tokens=500)

query = main_placeholder.text_input("Question: ")
print("gooddd")
if analyse_btn:
    print("gooddd d")
    loader = UnstructuredURLLoader(urls=urls)
    data = loader.load()
    # split data
    text_splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '.', ','],
        chunk_size=1000
    )
    
    docs = text_splitter.split_documents(data)
    # create embeddings and save it to FAISS index
    embeddings = OpenAIEmbeddings()
    vector_data = FAISS.from_documents(docs, embeddings)
    
    time.sleep(2)


    # Save index to a pickle file
    with open(file_path, "wb") as f:
        pickle.dump(vector_data, f)



if query:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            vectorstore = pickle.load(f)
            chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectorstore.as_retriever())
            result = chain({"question": query}, return_only_outputs=True)
            # result format --> {"answer": "", "sources": [] }
            st.header("Answer")
            st.write(result["answer"])

            
            sources = result.get("sources", "")
            if sources:
                st.subheader("Sources:")
                sources_list = sources.split("\n")  
                for source in sources_list:
                    st.write(source)
