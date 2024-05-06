import os 
import nltk
import sys
from docx import Document
from collections import Counter
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')

""" Function that counts how many words are in a file """
def count_words(file_path):
    try:
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                word_count = len(text.split())
                return word_count
        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            word_count = sum(len(paragraph.text.split()) for paragraph in doc.paragraphs)
            return word_count
        else:
            return "Unsupported file format. Please provide a .txt or .docx file."
    except FileNotFoundError:
        return "File not found."

""" Function that removes stopwords """
def remove_stopwords(text):
    nltk.download('stopwords')  # hada ytelechargi stop lists 
    stop_words = set(stopwords.words('english'))  # hada ysta3ml l english 
    cleaned_text = ' '.join(word for word in text.split() if word.lower() not in stop_words)
    return cleaned_text

""" function nta3 word search """
def get_word_details(word, cleaned_text):
    paragraphs = cleaned_text.split('.')  # Split the cleaned_text into paragraphs
    word_frequency = 0
    df = 0
    paragraph_ids = []
    tf = []

    for i, paragraph in enumerate(paragraphs):
        words = paragraph.split()
        word_count = words.count(word)
        if word_count > 0:
            df += 1
            paragraph_ids.append(i + 1)
            tf.append(word_count / len(words))
            word_frequency += word_count

    return word_frequency, df, paragraph_ids, tf




""" Function to show word frequency table """
def get_word_frequency_table_data(cleaned_text):
    words = cleaned_text.split()
    word_count = len(words)
    word_frequency = {}

    # Count word frequency
    for word in words:
        word_frequency[word] = word_frequency.get(word, 0) + 1

    # Calculate percentage of appearance
    word_percentage = {word: (count / word_count) * 100 for word, count in word_frequency.items()}

    # Sort word frequency by frequency in descending order
    sorted_word_frequency = sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)

    # Prepare data for QTableWidget
    table_data = []
    for word, frequency in sorted_word_frequency:
        percentage = word_percentage[word]
        table_data.append([word, frequency, f'{percentage:.2f}%'])

    return table_data