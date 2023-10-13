from flask import Flask, request, jsonify
import os
import openai
import sys
import shutil
import json
import pinecone
import spacy

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
nlp = spacy.load("en_core_web_md")

sys.path.append("../..")

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

openai.api_key = os.environ["OPENAI_API_KEY"]
pinecone.init(api_key=os.environ["PINECONE_API_KEY"],environment="gcp-starter")

docs_folder = "./docs/"  # The folder where PDFs will be stored
persist_directory = "docs/chroma/"  # Directory for Chroma vector storage

os.makedirs(docs_folder, exist_ok=True) # Create the /docs folder if it doesn't exist

with open('medicines.json', 'r') as file:
    medicines = json.load(file)

splits = []
for medicine in medicines:
    medicine_string = json.dumps(medicine)
    splits.append(medicine_string)

# print(splits)   # Print the list of JSON strings
# print(splits[2])

def text_to_vector(text):
    doc = nlp(text)
    vector = doc.vector
    return vector

vectorized_data = [text_to_vector(text) for text in splits]


index_name = "medicines"

if index_name not in pinecone.list_indexes():
    pinecone.create_index(name=index_name, dimension=64, metric="cosine")
# print(pinecone.list_indexes())

index = pinecone.Index(index_name)

items = [(str(i), vector) for i, vector in enumerate(vectorized_data)]
# print(items)
# index.upsert_items(items) # AttributeError: 'Index' object has no attribute 'upsert_items'

# index_info = pinecone.describe_index(index_name)
# print(index_info)
# Check the number of items (vectors) in the index
# num_items = index_info.stats.num_items
# print(f"Number of items in the index: {num_items}")

# os.makedirs(persist_directory, exist_ok=True)
# vectordb = Chroma.from_documents(
#     documents=splits,
#     embedding=embedding,
#     persist_directory=persist_directory
# )

# memory = ConversationBufferMemory(
#     memory_key="chat_history",
#     return_messages=True
# )
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
# retriever = vectordb.as_retriever()
# qa = ConversationalRetrievalChain.from_llm(
#     llm,
#     retriever=retriever,
#     memory=memory
# )
# sim_search = vectordb.similarity_search("pain killer", k=3)

# print(sim_search)
# # sim_search for future use to find answer from various chunks

# app = Flask(__name__)   # App created

# from flask_cors import CORS
# cors = CORS(app)

# @app.route('/', methods=['GET'])
# def welcome():
#     return "Explore PDF", 200

# # Route for uploading PDF files
# @app.route('/upload-pdf', methods=['POST'])
# def upload_pdf():
#     if 'pdf_file' not in request.files:
#         return jsonify({'error': 'No file part'})

#     pdf_file = request.files['pdf_file']
#     if pdf_file.filename == '':
#         return jsonify({'error': 'No selected file'})

#     clear_docs_folder()
#     # Save the uploaded PDF with its original filename in the /docs folder
#     pdf_filename = os.path.join(docs_folder, pdf_file.filename)
#     pdf_file.save(pdf_filename)

#     process_pdf(pdf_filename)

#     if vectordb is None:
#         return jsonify({'error': 'PDF not processed yet'}, 400)
#     else:
#         return jsonify({'message': 'File uploaded and processed successfully', 'filename': pdf_file.filename}, 201)

# def process_pdf(pdf_filename):
#     global vectordb
#     global qa

#     vectordb = None
#     qa = None

#     loader = PyPDFLoader(pdf_filename)
#     pages = loader.load()

#     # Split the document into pages using RecursiveCharacterTextSplitter
#     text_splitter = CharacterTextSplitter(
#         separator="\n",
#         chunk_size=1000,
#         chunk_overlap=50
#     )
#     docs = text_splitter.split_documents(pages)
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=500,
#         chunk_overlap=20
#     )
#     splits = text_splitter.split_documents(docs)

#     # Use Chroma to store vectors
    

# def clear_docs_folder():
#     for item in os.listdir(docs_folder):
#         item_path = os.path.join(docs_folder, item)
#         try:
#             if os.path.isfile(item_path):
#                 os.unlink(item_path)
#             elif os.path.isdir(item_path):
#                 shutil.rmtree(item_path)
#         except Exception as e:
#             print(f"Error deleting {item_path}: {e}")

# # Define a route for asking questions and getting responses
# @app.route('/ask-question', methods=['POST'])
# def ask_question():
#     data = request.get_json()
#     question = data.get('question')

#     if vectordb is None:
#         return jsonify({'error': 'PDF not processed yet'})

#     try:
#         result = qa({"question": question})
#         return jsonify({'response': result["answer"]}, 200)
#     except Exception as e:
#         return jsonify({'error': str(e)}, 400)


# if __name__ == '__main__':
#     app.run(debug=True)
