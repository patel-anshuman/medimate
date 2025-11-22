from flask import Flask, request, jsonify
import os
import openai
import sys
import shutil
import json

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from pymongo import MongoClient

sys.path.append("../..")

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

openai.api_key = os.environ["OPENAI_API_KEY"]

client = MongoClient(os.environ["MONGO_URL"]) # Mongo connectio string
db = client["medimate"] # Database name
medicines_collection = db["medicines"] # Collection name

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
    texts=splits, embedding=embedding, persist_directory=persist_directory
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

# Above code is 1 time, Below code everytime
# Searching items related to query (k = no. of meds in pdf = split by '\n')
# len_variable = lines if lines is not None and lines != 0 else 3
sim_search = vectordb.similarity_search("Amoxicillin, Paracetamol", k=3)
# print(sim_search)
sim_search_json = [json.loads(item.page_content) for item in sim_search]
print(sim_search_json) # data in json format

# # Collecting all unique ids from sim_search data
# id_set = set()
# for item in sim_search_json:
#     id_set.add(item['_id'])
# id_array = list(id_set)
# # print(id_array)

# medicine_data = []
# for id in id_array:
#     medicine = medicines_collection.find_one({"_id": id})
#     if medicine:
#         medicine_data.append(medicine)

# print(medicine_data)
# Reminder: Consult your doctor before using any medication.


# Forward this data to GPT function

# functions = [
#     {
#         "name": "get_medicine_id",
#         "description": "Get the id of medicine from data",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "data": {
#                     "type": "array",
#                     "items": {
#                         "type" : "object",
#                         "properties" : {
#                             "id": {
#                                 "type": "number",
#                                 "description": "Product ID, e.g. 1"
#                             }
#                         },
#                         "required" : ["id"]
#                     }
#                 }
#             },
#             "required": ["data"]    
#         },
#     }
# ]

# query = """"""

# completion = openai.ChatCompletion.create(
#     model= "gpt-3.5-turbo-0613",
#     messages = [{"role": "user", "content": f"{sim_search}"}],
#     functions = functions,
#     function_call = "get_medicine_id"
# )

# output = completion.choices[0].message
# print(output)
