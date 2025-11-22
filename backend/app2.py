from flask import Flask, request, jsonify
from flask_cors import CORS
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
docs_folder = "./docs/"
pres_persist_directory = "/docs/pres_chroma"

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
med_splits = []
for medicine in medicines:
    medicine_string = json.dumps(medicine)
    med_splits.append(medicine_string)

med_persist_directory = "docs/chroma/"
embedding = OpenAIEmbeddings()
med_vectordb = Chroma.from_texts(
    texts=med_splits, embedding=embedding, persist_directory=med_persist_directory
)

# General Chat Conversation Chain
memory = ConversationBufferMemory()
memory.save_context(
    {
        "input": "Bot Instructions: 1. Introduction: Start by introducing yourself as a healthcare assistant from MediMate. 🌡️🏥 2. Welcome: Always begin with a warm welcome message. 3. Symptom Assessment: Prompt users to share their symptoms. Ask for details and offer guidance. 4. Specialization: If necessary, guide users to a specialist or department and explain the next steps. 5. Emergency Response: In emergencies, prioritize and recommend dialing 108 (or the local emergency number) for an ambulance. 6. One Question Rule: Encourage users to ask one health-related question at a time. 7. Set Expectations: Clarify that the bot provides health guidance, not personalized medical advice. 8. Thank You: Remind users to express gratitude and acknowledge their appreciation. Our aim is to provide efficient and helpful healthcare assistance."
    },
    {
        "output": "Welcome to MediMate! How can I assist you with your health today?"
    },
)
chat_response = ChatOpenAI(temperature=0.9)
conversation = ConversationChain(llm=chat_response, memory=memory, verbose=False)

app = Flask(__name__)   # App created

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
    elif 'pdf_file' in request.files:
        # The received file is PDF, call the pdf_chat() function
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'No file part'})

        pdf_file = request.files['pdf_file']
        if pdf_file.filename == '':
            return jsonify({'error': 'No selected file'})

        clear_docs_folder()
        pdf_filename = os.path.join(docs_folder, pdf_file.filename)
        pdf_file.save(pdf_filename)

        return jsonify({'msg': pdf_filename.filename})
        pdf_chat(pdf_filename)
        
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
    loader = PyPDFLoader(pdf_file)
    pages = loader.load()

    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=50, length_function=len
    )
    docs = text_splitter.split_documents(pages)  # separated by paras
    # print(docs)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    pres_splits = text_splitter.split_documents(docs)

    pres_vectordb = Chroma.from_documents(
        documents=pres_splits, embedding=embedding, persist_directory=pres_persist_directory
    )
    # Delete pdf index from pinecone before creating new one

    # Retrieve meds from prescription
    qa_chain = RetrievalQA.from_chain_type(
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
        retriever = pres_vectordb.as_retriever()
    )
    extract_med = qa_chain({"query": "meds name only"})
    # extract_med["result"]
    # print(extract_med)
    # return jsonify({"message": extract_med["result"]}), 200

    # Sim search on med vectordb to get ids
    sim_search = med_vectordb.similarity_search(extract_med["result"], k=5)
    # print(sim_search)
    sim_search_json = [json.loads(item.page_content) for item in sim_search]
    # print(sim_search_json) # data in json format

    # Collecting all unique ids from sim_search data
    id_set = set()
    for item in sim_search_json:
        id_set.add(item['_id'])
    id_array = list(id_set)
    # print(id_array)

    # Mongo search for more details
    medicine_data = []
    for id in id_array:
        medicine = medicines_collection.find_one({"_id": id})
        if medicine:
            medicine_data.append(medicine)

    # print(medicine_data)
    return jsonify({"message": "You can buy the medicines from below:", "recommendation": medicine_data}), 200

def clear_docs_folder():
    # Delete all files within the 'docs' folder
    for item in os.listdir(docs_folder):
        item_path = os.path.join(docs_folder, item)
        try:
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            print(f"Error deleting {item_path}: {e}")

    # Delete the 'docs/pres_chroma' folder
    try:
        shutil.rmtree(pres_persist_directory)
    except Exception as e:
        print(f"Error deleting {pres_persist_directory}: {e}")

if __name__ == '__main__':
    app.run(debug=True)