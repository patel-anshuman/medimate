# **MediMate**
MediMate is a friendly health assistant chatbot designed to provide comprehensive support. From scheduling doctor appointments, extracting prescription details from PDFs, and offering emergency assistance, to dispensing health tips and home remedies, MediMate is your reliable and friendly companion for all your health-related needs.

## **Platform Access**

Access the MediMate platform through **[MediMate](https://medimate-eight.vercel.app/)**

## **Feature Walkthrough**

Watch my guided video walkthrough: **[Link to feature walkthrough @YouTube](https://youtu.be/MqoRefGciUs)**

## Key Features
- appointment scheduling
- prescription pdf comprehensive medication help
- emergency assistance
- health tips and home remedies
- chat history 

## **Installation & Getting Started**
- Clone the repository:
  ```bash
  git clone https://github.com/patel-anshuman/medimate.git
  ```

### **Frontend**
- Install dependencies: ```npm install```
- Start the guided tour: ```npm start```

### **Backend**
- Create a virtual environment: ```python -m venv venv```
- On Windows: ```venv\Scripts\activate```
- On macOS and Linux: ```source venv/bin/activate```
- Install Backend Dependencies: ```pip install -r requirements.txt```
- Run the Backend App: ```python app.py```

## **User Journey**

### 1. Initiate Chat
- The user launches the Health Assistant Chat Application.
- They are greeted with a warm welcome message from the healthcare assistant.

### 2. Discuss Health
- Users can discuss their health concerns, and symptoms, or ask health-related questions.
- The chatbot will assess the user's symptoms and provide guidance based on the information provided.

### 3. Appointment Request
- If the symptoms indicate a need for a specialist, the chatbot guides the user to the relevant department or specialist.
- Users can request appointments with doctors through the chat.

### 4. Emergency Assistance
- In case of a perceived emergency condition, the chatbot recommends dialling 108 (or the local emergency number) to call an ambulance without further questions.

### 5. Chat History
- The conversation history is saved and can be accessed by the user if they need to review previous discussions.

### 6. Medicines Inquiry
- Users can send a PDF file containing prescription details to inquire about medicines.
- The chatbot processes the prescription, extracts medicine information, and provides links to purchase them.

### 7. Thank You
- Users are prompted to say "Thank you" when they are done.
- The chatbot acknowledges their gratitude and provides closing remarks.


## **Methods**

### `general()` Method

- Description: Handles general queries and responses within the Health Assistant Chat Application. It provides answers to a wide range of health-related questions and inquiries.
- Use Case: Users can seek answers to health-related questions, receive information about symptoms, treatments, and general healthcare advice.
- Input Parameters: The primary input parameter is the user's question or query.
- Output: Generates responses based on the user's queries, offering information, guidance, and assistance for general healthcare topics.
- Example Usage: `response = general("What are the symptoms of the flu?")`

### `pdf_chat()` Method

- Description: Specifically handles PDF files containing prescription details. It processes the prescription, extracts information about prescribed medicines, and provides relevant links for purchasing these medicines. Additionally, it includes details such as images, prices, and names.
- Use Case: Users can use this method to inquire about medicines prescribed in their medical documents and access convenient purchase links.
- Input Parameters: The primary input parameter is the PDF file containing prescription details.
- Output: Generates a response with information about prescribed medicines, offering purchase links for each medicine, along with supplementary details like images, prices, and names.
- Example Usage: `response = pdf_chat(pdf_file)`

## **Technology Stacks**
- Front-end: React.js
- Back-end: Python, Flask
- Database: MongoDB (Chat History), Pinecone (Vector DB)


