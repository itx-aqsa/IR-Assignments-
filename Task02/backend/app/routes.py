# Import necessary libraries
from flask import Blueprint, request, jsonify  # Flask-related imports
import os  # For interacting with the file system
import math  # For mathematical operations like log() in IDF computation
from config import Config  # Importing configuration settings (e.g., document folder path)

# Initialize Flask Blueprint for this module
main = Blueprint('main', __name__)

# The folder path where documents are stored, fetched from the configuration
folder_path = Config.DOCUMENT_FOLDER

# Function to load documents from the specified folder
def load_documents():
    """
    Loads all documents from the folder specified in Config.DOCUMENT_FOLDER
    and returns a dictionary with the filename as the key and document content as the value.
    """
    docs = {}
    # List all files in the specified folder
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)  # Get the full file path
        with open(file_path, 'r') as f:  # Open each document
            content = f.read()  # Read document content
            docs[file] = content  # Store the content in the dictionary with filename as key
    return docs  # Return the dictionary of documents

# Load documents into memory (this will be used by other functions)
documents = load_documents()

# Function to perform keyword matching for document ranking
def keyword_matching(query, documents):
    """
    This function matches query keywords to words in each document.
    It ranks documents based on the number of matching keywords.
    """
    # Step 1: Split the query into individual keywords and convert them to lowercase
    query_keywords = query.lower().split()
    # Step 2: Create a dictionary to store ranking scores for each document
    rankings = {}
    # Step 3: Loop through each document
    for doc_name, content in documents.items():
        # Split document content into words and convert to lowercase
        content_words = content.lower().split()    
        # Initialize match count for this document
        match_count = 0     
        # Step 4: Loop through each keyword and check if it exists in the document content
        for keyword in query_keywords:
            if keyword in content_words:  # If keyword is found in the document
                match_count += 1  # Increment match count      
        # Step 5: Store the match count as the document's score
        rankings[doc_name] = match_count
    # Step 6: Sort documents by match count (highest to lowest)
    ranked_docs = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
    return ranked_docs  # Return ranked documents based on matches

# Function to compute Term Frequency (TF) for a document
def compute_tf(doc):
    """
    Computes the Term Frequency (TF) for each word in the document.
    TF is calculated as the number of occurrences of a word divided by the 
    total number of words in the document.
    """
    words = doc.split()  # Split the document into words
    tf_dict = {}  # Dictionary to store the term frequencies
    total_words = len(words)  # Get total number of words in the document
    
    # Count the occurrences of each word in the document
    for word in words:
        word = word.lower()  # Convert word to lowercase for case-insensitivity
        tf_dict[word] = tf_dict.get(word, 0) + 1  # Increment word count in dictionary
    
    # Normalize the word frequencies by dividing by the total number of words
    for word in tf_dict:
        tf_dict[word] = tf_dict[word] / total_words  # TF calculation
    
    return tf_dict  # Return the Term Frequency dictionary

# Function to compute Inverse Document Frequency (IDF) for words across all documents
def compute_idf(documents):
    """
    Computes the Inverse Document Frequency (IDF) for each unique word across all 
    documents. IDF helps to determine the importance of words based on how frequently
    they appear in the entire corpus.
    """
    N = len(documents)  # Total number of documents
    idf_dict = {}  # Dictionary to store IDF values for each word
    
    # Step 1: Loop through each document and calculate the frequency of each word across documents
    for content in documents.values():
        words = set(content.split())  # Get unique words in the document
        for word in words:
            word = word.lower()  # Convert to lowercase for case-insensitivity
            idf_dict[word] = idf_dict.get(word, 0) + 1  # Count the number of documents containing each word
    
    # Step 2: Calculate IDF for each word using the formula:
    # IDF(w) = log(N / DF(w)), where DF(w) is the document frequency of the word
    for word in idf_dict:
        idf_dict[word] = math.log(N / idf_dict[word])  # IDF calculation
    
    return idf_dict  # Return the Inverse Document Frequency dictionary

# Function to compute TF-IDF for a query and rank documents accordingly
def compute_tfidf(query, documents):
    """
    Computes the Term Frequency-Inverse Document Frequency (TF-IDF) score for 
    each document based on the query. Ranks documents by the sum of TF-IDF scores 
    for each keyword in the query.
    """
    idf_dict = compute_idf(documents)  # Get the IDF values for words across all documents
    query_keywords = query.lower().split()  # Split the query into keywords
    # Step 1: Create a dictionary to store TF-IDF scores for each document
    rankings = {}
    # Step 2: Loop through each document and calculate its TF-IDF score based on the query
    for doc_name, content in documents.items():
        tf_dict = compute_tf(content)  # Compute the TF for the document
        tfidf_score = 0  # Initialize TF-IDF score for this document
        # Step 3: For each keyword in the query, compute its TF-IDF contribution to the document
        for word in query_keywords:
            if word in tf_dict and word in idf_dict:
                tfidf = tf_dict[word] * idf_dict[word]  # TF-IDF calculation
                tfidf_score += tfidf  # Accumulate the TF-IDF score
        # Step 4: Store the computed TF-IDF score for the document
        rankings[doc_name] = tfidf_score
    # Step 5: Sort documents based on their TF-IDF score (highest to lowest)
    ranked_docs = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
    return ranked_docs  # Return ranked documents based on TF-IDF score

# Flask route to handle the search request
@main.route('/search', methods=['POST'])
def search_documents():
    """
    This route handles POST requests for searching documents. It accepts a query and a ranking method (1 or 2).
    - Method 1: Keyword matching
    - Method 2: TF-IDF ranking
    """
    # Get the JSON data from the request body
    data = request.get_json()
    query = data.get('query')  # Get the search query from the request
    method = data.get('method')  # Get the ranking method from the request
    
    # Step 1: Check if the query is provided in the request
    if not query:
        return jsonify({"error": "Query is required"}), 400  # Return error if no query is provided
    
    # Step 2: Perform the ranking based on the method
    if method == '1':
        ranked_docs = keyword_matching(query, documents)  # Use keyword matching
    elif method == '2':
        ranked_docs = compute_tfidf(query, documents)  # Use TF-IDF ranking
    else:
        return jsonify({"error": "Invalid ranking method"}), 400  # Return error for invalid method
    
    # Step 3: Prepare the response in JSON format with document names and scores
    response = [{"document": doc_name, "score": score} for doc_name, score in ranked_docs]
    
    return jsonify(response)  # Return the ranked documents as JSON response