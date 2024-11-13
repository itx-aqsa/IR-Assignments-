from flask import Blueprint, request, jsonify
import os
from sortedcontainers import SortedDict

main = Blueprint('main', __name__)

folder_path = "documents"
word_file_dict = SortedDict()
stop_words = {"it", "the", "as", "a", "and", "is", "in", "at", "of", "to", "on", "for", "with", "by", "that", "an"}

# Populate the dictionary on startup
def populate_word_file_dict():
    word_file_dict.clear()
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r') as file:
                content = file.read().split()
                for word in content:
                    word = word.lower()
                    if word in stop_words:
                        continue
                    if word in word_file_dict:
                        if file_name not in word_file_dict[word]:
                            word_file_dict[word].append(file_name)
                    else:
                        word_file_dict[word] = [file_name]

populate_word_file_dict()


# Binary search function to find a word in the SortedDict keys
def binary_search_word(word):
    words = list(word_file_dict.keys())  # Convert the SortedDict keys to a list
    low, high = 0, len(words) - 1

    while low <= high:
        mid = (low + high) // 2
        if words[mid] == word:
            return set(word_file_dict[words[mid]])  # Return a set of files containing the word
        elif words[mid] < word:
            low = mid + 1
        else:
            high = mid - 1
    
    return set()  # Return an empty set if the word is not found


@main.route('/search', methods=['POST'])
def search():
    query = request.json.get('query', '').lower()
    words = query.split()
    
    # Initialize a set to hold the filenames that match all words
    result_files = None
    
    for word in words:
        if word in stop_words:  # Skip stop words entirely
            continue
        
        # Use binary search for the current word and get the set of files
        current_files = binary_search_word(word)
        
        # If it's the first word, initialize result_files with the files for this word
        if result_files is None:
            result_files = current_files
        else:
            # Intersect with the files of the current word
            result_files &= current_files
    
    # Convert the result_files set back to a sorted list or return an empty list if no results
    return jsonify({"results": sorted(result_files) if result_files else []})




@main.route('/get_file_content', methods=['POST'])
def get_file_content():
    file_name = request.json.get('file_name')
    file_path = os.path.join(folder_path, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return jsonify({"content": content})
    else:
        return jsonify({"error": "File not found"}), 404
