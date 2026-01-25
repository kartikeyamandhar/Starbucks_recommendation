"""
Flask API to serve frontend queries
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from pipeline import query_products
import sys

app = Flask(__name__)
CORS(app)  # Allow frontend to call this API

@app.route('/api/query', methods=['POST'])
def handle_query():
    """
    Endpoint to process a query and return ranked products
    """
    try:
        data = request.json
        query_text = data.get('query')
        
        if not query_text:
            return jsonify({'error': 'No query provided'}), 400
        
        # Call your existing pipeline
        print(f"Processing query: {query_text}", file=sys.stderr)
        products = query_products(query_text)
        
        # Format response for frontend
        response = {
            'products': products,
            'query': query_text,
            'count': len(products)
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    print("Starting Flask API server...")
    print("API will be available at http://localhost:5000")
    app.run(host='0.0.0.0', port=5001, debug=True)