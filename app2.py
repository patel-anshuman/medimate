import os
import sys
import json
import shutil
from typing import List, Dict, Any, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA, ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

# ==========================================
# Configuration & Environment Variables
# ==========================================
load_dotenv(find_dotenv())

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MONGO_URL = os.environ.get("MONGO_URL")

# Directory Paths
DOCS_FOLDER = "./docs/"
PRES_PERSIST_DIRECTORY = "docs/pres_chroma"
MED_PERSIST_DIRECTORY = "docs/chroma/"
MEDICINES_FILE = "medicines.json"

# Ensure OpenAI Key is set
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

openai_api_key = OPENAI_API_KEY  # For langchain if needed implicitly

# ==========================================
# Initialization & Setup
# ==========================================

def init_mongo_connection() -> Any:
    """Initialize MongoDB connection."""
    if not MONGO_URL:
        raise ValueError("MONGO_URL not found in environment variables.")
    client = MongoClient(MONGO_URL)
    db = client["medimate"]
    return db["medicines"]

def init_med_vector_store() -> Chroma:
    """
    Initialize the vector store for medicines.
    Reads from medicines.json, creates embeddings, and returns the Chroma vector store.
    """
    if not os.path.exists(MEDICINES_FILE):
        print(f"Warning: {MEDICINES_FILE} not found. Medicine recommendation might not work.")
        return None

    with open(MEDICINES_FILE, "r") as file:
        medicines = json.load(file)

    med_splits = [json.dumps(medicine) for medicine in medicines]
    
    embedding = OpenAIEmbeddings()
    vector_db = Chroma.from_texts(
        texts=med_splits, 
        embedding=embedding, 
        persist_directory=MED_PERSIST_DIRECTORY
    )
    return vector_db

def init_conversation_chain() -> ConversationChain:
    """Initialize the general healthcare assistant conversation chain."""
    memory = ConversationBufferMemory()
    memory.save_context(
        {
            "input": (
                "Bot Instructions:\n"
                "1. Introduce Yourself: Begin by introducing yourself as a healthcare assistant from MediMate. 🌡️🏥\n"
                "2. Welcome Message: Always start with a warm welcome message.\n"
                "3. Symptom Assessment: Assess the user's symptoms when prompted. Ask for details and provide guidance.\n"
                "4. Specialization: If needed, guide the user to a specialist or department, and explain next steps.\n"
                "5. Emergency Response: In emergencies, prioritize and suggest dialing 108 (or local emergency number) for an ambulance.\n"
                "6. One Question at a Time: Encourage users to ask one health-related question at a time.\n"
                "7. Set Expectations: Clarify that the bot provides health guidance, not personalized medical advice.\n"
                "8. Thank You Message: Remind users to say Thank you and acknowledge their gratitude.\n"
                "Our goal is efficient and helpful healthcare assistance."
            )
        },
        {
            "output": "Welcome to MediMate! How can I assist you with your health today?"
        },
    )
    chat_llm = ChatOpenAI(temperature=0.9)
    return ConversationChain(llm=chat_llm, memory=memory, verbose=False)

# Global Instances
medicines_collection = init_mongo_connection()
med_vectordb = init_med_vector_store()
conversation_chain = init_conversation_chain()
embedding_function = OpenAIEmbeddings()

app = Flask(__name__)
CORS(app)

# ==========================================
# Helper Functions
# ==========================================

def process_pdf_and_create_vector_store(pdf_path: str) -> Chroma:
    """
    Loads a PDF, splits it into chunks, and creates a temporary vector store.
    """
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    # Split by character first (paragraphs)
    char_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=50, length_function=len
    )
    docs = char_splitter.split_documents(pages)

    # Further split for embeddings
    recursive_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    pres_splits = recursive_splitter.split_documents(docs)

    pres_vectordb = Chroma.from_documents(
        documents=pres_splits, 
        embedding=embedding_function, 
        persist_directory=PRES_PERSIST_DIRECTORY
    )
    return pres_vectordb

def extract_medicines_from_prescription(pres_vectordb: Chroma) -> str:
    """
    Queries the prescription vector store to extract medicine names.
    """
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
        retriever=pres_vectordb.as_retriever()
    )
    response = qa_chain({"query": "meds name only"})
    return response["result"]

def find_medicine_recommendations(medicine_names_text: str) -> List[Dict]:
    """
    Searches for medicines in the medicine vector store and retrieves details from MongoDB.
    """
    if not med_vectordb:
        return []

    # Similarity search to find relevant medicines
    sim_search = med_vectordb.similarity_search(medicine_names_text, k=5)
    sim_search_json = [json.loads(item.page_content) for item in sim_search]

    # Collect unique IDs
    unique_ids = list({item['_id'] for item in sim_search_json})

    # Fetch full details from MongoDB
    recommendations = []
    for med_id in unique_ids:
        medicine = medicines_collection.find_one({"_id": med_id})
        if medicine:
            recommendations.append(medicine)
    
    return recommendations

# ==========================================
# Routes
# ==========================================

@app.route('/', methods=['GET'])
def welcome():
    return "MediMate Backend is Running", 200

@app.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint. Handles both general text questions and PDF prescription uploads.
    """
    # 1. Handle JSON Question (General Chat)
    if request.is_json:
        json_data = request.get_json()
        question = json_data.get('question', '')
        
        if not question:
            return jsonify({"message": "Question is required"}), 400
        
        try:
            response_message = conversation_chain.predict(input=question)
            return jsonify({"message": response_message}), 200
        except Exception as e:
            return jsonify({"error": f"Error processing request: {str(e)}"}), 500

    # 2. Handle PDF Upload (Prescription Analysis)
    elif 'pdf_file' in request.files:
        pdf_file = request.files['pdf_file']

        if not pdf_file.filename.endswith('.pdf'):
            return jsonify({'error': 'Invalid file format. Please upload a PDF.'}, 415)
        
        try:
            # Save temporarily
            temp_filename = f"temp_{pdf_file.filename}"
            pdf_file.save(temp_filename)

            try:
                # Process PDF
                pres_vectordb = process_pdf_and_create_vector_store(temp_filename)
                
                # Extract Medicines
                extracted_meds_text = extract_medicines_from_prescription(pres_vectordb)
                
                # Find Recommendations
                recommendations = find_medicine_recommendations(extracted_meds_text)
                
                return jsonify({
                    "message": "Based on the prescription, here are the recommended medicines:", 
                    "recommendation": recommendations,
                    "extracted_text": extracted_meds_text # Optional: return what was found
                }), 200

            finally:
                # Cleanup
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                # Note: You might want to cleanup the chroma persistence directory too if it's temporary per request

        except Exception as e:
            return jsonify({"error": f"Error processing PDF: {str(e)}"}), 500

    else:
        return jsonify({'error': 'Unsupported request format. Send JSON with "question" or form-data with "pdf_file".'}, 415)

if __name__ == '__main__':
    app.run(debug=True)