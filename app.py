from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from ask import query_documents
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for Firebase frontend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get question from request
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        question = data['question'].strip()
        if not question:
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        logger.info(f"Received question: {question}")
        
        # Query documents and get answer
        answer = query_documents(question)
        
        logger.info(f"Generated answer: {answer[:100]}...")
        
        return jsonify({'answer': answer})
    
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'CMMC Compliance Chatbot API is running',
        'endpoints': {
            '/chat': 'POST - Send a question to the chatbot',
            '/health': 'GET - Check API health'
        }
    })

if __name__ == '__main__':
    # Check if vector store exists
    if not os.path.exists('./chroma_db'):
        logger.warning("ChromaDB not found. Please run embed_documents.py first.")
    
    # Get port from environment variable for Render.com compatibility
    port = int(os.environ.get('PORT', 10000))  # Render.com expects port 10000 by default
    logger.info(f"Starting server on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)