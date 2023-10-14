from flask import Flask, request, jsonify
import os
import openai
import sys
import shutil
import json

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

sys.path.append("../..")

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

openai.api_key = os.environ["OPENAI_API_KEY"]

# Read medicine.json file
with open("medicines.json", "r") as file:
    medicines = json.load(file)

# splits -> array of strings(each med data)
splits = []
for medicine in medicines:
    medicine_string = json.dumps(medicine)
    splits.append(medicine_string)

persist_directory = "docs/chroma/"
embedding = OpenAIEmbeddings()
vectordb = Chroma.from_texts(
    texts=splits, 
    embedding=embedding, 
    persist_directory=persist_directory
)


# Defining (LLM for embeds, retriever, memory) for QA Chain
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
# retriever = vectordb.as_retriever()
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
# # QA Chain to store conversation
# qa = ConversationalRetrievalChain.from_llm(
#     llm, 
#     retriever=retriever, 
#     memory=memory
# )

# Searching items related to query (no. = 3)
sim_search = vectordb.similarity_search("cold fever", k=3)
print(sim_search)

# Forward this data to GPT function




