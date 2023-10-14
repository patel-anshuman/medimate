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
from langchain.chains import RetrievalQA, ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from pymongo import MongoClient

sys.path.append("../..")    # relative directory path

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# Loading enviroment variables
openai.api_key = os.environ["OPENAI_API_KEY"] # OpenAI Key
client = MongoClient(os.environ["MONGO_URL"]) # Mongo connectio string
db = client["medimate"] # Database name
medicines_collection = db["medicines"] # Collection name

# Read file & create vector -- Replace later by pinecone
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

# General Chat Conversation Chain
memory = ConversationBufferMemory()
memory.save_context(
    {
        "input": "Bot Instructions:\n1. Introduce Yourself: Start by introducing yourself as a healthcare assistant from MediMate. 🌡️🏥\n2. Welcome Message: Always initiate the conversation with a warm welcome message.\n3. Symptom Assessment: Assess the user's symptoms when prompted. Ask for symptom details and provide guidance based on the information given.\n4. Specialization: If symptoms indicate the need for a specialist, guide the user to the relevant department or specialist, and provide information on next steps.\n5. Emergency Response: If there's an emergency condition, make it a priority. Recommend dialing 108 (or the local emergency number) to call an ambulance without further questions.\n6. One Question at a Time: Remind the user to ask one health-related question at a time for focused and detailed assistance.\n7. Set Expectations: Clearly state that the bot is for health-related queries and guidance, not for personalized medical advice.\n8. Thank You Message: Prompt users to say Thank you when they're done. Acknowledge their gratitude.\nRemember, the goal is to provide efficient and helpful healthcare assistance"
    },
    {
        "output": "Welcome to MediMate! How can I assist you with your health today?"
    },
)
chat_response = ChatOpenAI(temperature=0.9)
conversation = ConversationChain(llm=chat_response, memory=memory, verbose=False)

app = Flask(__name__)   # App created

from flask_cors import CORS
cors = CORS(app)

@app.route('/', methods=['GET'])
def welcome():
    return "MediMate", 200

@app.route('/chat', methods=['POST'])
def chat():
    if request.is_json:
        # The received file is JSON, call the general() function
        json_data = request.get_json()
        question = json_data.get('question', '')  # Assuming the question field is in the JSON
        response = general(question)
    elif request.files and 'pdf_file' in request.files:
        # The received file is a PDF, call the pdf_chat() function
        pdf_file = request.files['pdf_file']
        response = pdf_chat(pdf_file)
    else:
        # Handle other cases or return an error message
        response = jsonify({'error': 'Unsupported file format or request.'}, 415)
        
    return response

def general(question):
    # Logic for handling JSON data
    # You can access the 'question' parameter here
    if not question:
        return jsonify({"message": "Question is required"}), 400
    
    try:
        response_message = conversation.predict(input=question)
        # print(response_message)
        return jsonify({"message": response_message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def pdf_chat(pdf_file):
    # Logic for handling PDF file
    # You can access the 'pdf_file' parameter here
    pass

if __name__ == '__main__':
    app.run(debug=True)