# -*- coding: utf-8 -*-
"""
Khmer News Classification System
===============================
Advanced Text Classification Platform for Khmer Language News Articles

This application provides a comprehensive Natural Language Processing solution
for automated categorization of Khmer news articles using state-of-the-art
machine learning techniques including FastText embeddings and Support Vector
Machine classification.

Author: FYP Research Team
Version: 2.0.0
Date: May 31, 2025
License: Academic Research Use
"""

import streamlit as st
import joblib
import numpy as np
import pandas as pd
import os
import json
import PyPDF2
import time
import unicodedata
import re
import collections
from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass
from enum import Enum
import hashlib
from datetime import datetime



# Configure page settings
st.set_page_config(
    page_title="KH News Multi-ClassClassifier",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Make container wider and fill screen */
    .main .block-container {
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1rem;
    }
    
    /* Remove default sidebar space when collapsed */
    .css-1d391kg {
        padding-left: 1rem;
    }
    
    /* Ensure full width usage */
    .stApp > header {
        background-color: transparent;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .input-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .result-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .prediction-card {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 8px 25px rgba(40,167,69,0.3);
        transform: translateY(-5px);
    }
    .confidence-bar {
        background: #e9ecef;
        height: 25px;
        border-radius: 12px;
        overflow: hidden;
        margin: 0.5rem 0;
        position: relative;
    }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    .stat-item {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    .stat-item:hover {
        transform: translateY(-2px);
    }
    .feature-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f9f9f9;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .stProgress .st-bo {
        background-color: #667eea;
    }
    .input-method-selector {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
        justify-content: center;
    }
    .method-card {
        flex: 1;
        max-width: 300px;
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .method-card:hover {
        border-color: #667eea;
        transform: translateY(-3px);
        box-shadow: 0 4px 20px rgba(102,126,234,0.15);
    }
    .method-card.active {
        border-color: #667eea;
        background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
    }
    
    /* Custom dialog width for wider popup */
    div[data-testid="stDialog"] {
        width: 98vw !important;
        max-width: 1800px !important;
    }
    
    div[data-testid="stDialog"] > div {
        width: 100% !important;
        max-width: none !important;
    }
    
    /* Additional popup width styling */
    .stDialog {
        width: 98vw !important;
        max-width: 1800px !important;
    }
    
    [data-testid="stDialog"] .stDialog {
        width: 98vw !important;
    }
    
    /* Force full width for dialog content */
    [data-testid="stDialog"] .element-container {
        width: 100% !important;
    }
    
    [data-testid="stDialog"] .stMarkdown {
        width: 100% !important;
    }
    
    /* Ultra-wide popup overrides */
    section[data-testid="stDialog"] {
        width: 95vw !important;
        max-width: 1600px !important;
    }
    
    section[data-testid="stDialog"] > div {
        width: 100% !important;
    }
    
    /* Container overrides for modal */
    [data-testid="stDialog"] .block-container {
        max-width: 100% !important;
        width: 100% !important;
    }
    
    [data-testid="stDialog"] .main {
        width: 100% !important;
    }
    
    /* Custom prediction button styling */
    div[data-testid="stButton"] > button[key="prediction_card"] {
        background: #28a745 !important;
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
        color: white !important;
        border: none !important;
        padding: 1.5rem 2rem !important;
        border-radius: 15px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(40,167,69,0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        min-height: 80px !important;
    }
    
    /* Additional fallback selectors for prediction button */
    button[data-testid*="prediction"] {
        background: #28a745 !important;
        color: white !important;
    }
    
    .stButton > button:has-text("📂") {
        background: #28a745 !important;
        color: white !important;
    }
    
    div[data-testid="stButton"] > button[key="prediction_card"]:hover {
        background: linear-gradient(135deg, #218838 0%, #1ea085 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(40,167,69,0.4) !important;
    }
    
    div[data-testid="stButton"] > button[key="prediction_card"]:focus {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
        box-shadow: 0 0 0 3px rgba(40,167,69,0.25) !important;
    }
</style>""", unsafe_allow_html=True)

# Configuration and constants
class Config:
    """Application configuration constants"""
    # Dynamic model path detection
    @staticmethod
    def get_model_directory():
        """Dynamically find the model directory based on current working directory or common locations"""
        # First, try to find relative to current working directory
        possible_paths = [
            os.path.join(os.getcwd(), "Demo_model"),
            os.path.join(os.getcwd(), "models"),
            os.path.join(os.getcwd(), "model"),
            os.path.join(os.path.dirname(__file__), "Demo_model"),
            os.path.join(os.path.dirname(__file__), "models"),
            os.path.join(os.path.dirname(__file__), "model"),
            # Common project structure paths
            os.path.join(os.path.expanduser("~"), "Documents", "DEV", "Demo_model"),
            os.path.join(os.path.expanduser("~"), "Desktop", "Demo_model"),
            os.path.join(os.path.expanduser("~"), "Downloads", "Demo_model"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.path.isdir(path):
                # Verify it contains expected model files
                expected_files = ["svm_model.joblib", "config.json"]
                if all(os.path.exists(os.path.join(path, f)) for f in expected_files):
                    return path
        
        # If no valid directory found, return None
        return None
    
    # Initialize model directory
    MODEL_DIR = get_model_directory.__func__() or os.path.join(os.getcwd(), "Demo_model")
    
    if not os.path.exists(MODEL_DIR):
        st.error(f"""
        Model directory not found!
        
        Please ensure your model files are in one of these locations:
        • Current directory: {os.path.join(os.getcwd(), "Demo_model")}
        • Same folder as script: {os.path.join(os.path.dirname(__file__) if '__file__' in globals() else os.getcwd(), "Demo_model")}
        • Home Documents: {os.path.join(os.path.expanduser("~"), "Documents", "DEV", "Demo_model")}
        • Desktop: {os.path.join(os.path.expanduser("~"), "Desktop", "Demo_model")}
        
        Required files:
        • svm_model.joblib
        • config.json
        """)
        st.stop()
    
    SVM_MODEL_PATH = os.path.join(MODEL_DIR, "svm_model.joblib")
    CONFIG_PATH = os.path.join(MODEL_DIR, "config.json")
    # FastText model is in the root directory, not in MODEL_DIR
    FASTTEXT_MODEL_PATH = os.path.join(os.getcwd(), "cc.km.300.bin")
    
    # Training data paths (if needed)
    X_TRAIN_PATH = os.path.join(MODEL_DIR, "X_train_fasttext.joblib")
    X_TEST_PATH = os.path.join(MODEL_DIR, "X_test_fasttext.joblib")
    Y_TRAIN_PATH = os.path.join(MODEL_DIR, "y_train_fasttext.joblib")
    Y_TEST_PATH = os.path.join(MODEL_DIR, "y_test_fasttext.joblib")
    
    CATEGORIES = ["economic", "environment", "health", "politic", "sport", "technology"]
    CATEGORY_LABELS = {
        "economic": "Economic",
        "environment": "Environment", 
        "health": "Health",
        "politic": "Politics",
        "sport": "Sports",
        "technology": "Technology"
    }
    
    # Khmer character sets for preprocessing
    KHCONST = set(u'កខគឃងចឆជឈញដឋឌឍណតថទធនបផពភមយរលវឝឞសហឡអឣឤឥឦឧឨឩឪឫឬឭឮឯឰឱឲឳ')
    KHVOWEL = set(u'឴឵ាិីឹឺុូួើឿៀេែៃោៅ\u17c6\u17c7\u17c8')
    KHSUB = set(u'្')
    KHSYM = set('៕។៛ៗ៚៙៘៖«»')
    KHNUMBER = set(u'០១២៣៤៥៦៧៨៩')
    ARABIC_NUMBER = set('0123456789')
    LATIN_CHARS = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    PUNCTUATION = set('"!@#$%^&*()-_+=[]{};\'\"\|,.<>?/`~፡.,፣;፤፥፦፧፪፠፨')

class CategoryType(Enum):
    """Enumeration for news categories"""
    ECONOMIC = "economic"
    ENVIRONMENT = "environment"
    HEALTH = "health"
    POLITIC = "politic"
    SPORT = "sport"
    TECHNOLOGY = "technology"

@dataclass
class ClassificationResult:
    """Data class for classification results"""
    prediction: str
    confidence: Dict[str, float]
    processing_time: float
    cleaned_text: str
    segmented_text: str
    embedding: np.ndarray
    timestamp: datetime
    input_text: str
    text_statistics: Dict[str, Any]
    prediction_id: str

class TextProcessor:
    """Advanced text processing utilities for Khmer language"""
    
    @staticmethod
    def normalize_khmer_text(text: str) -> str:
        """Normalize Khmer text using Unicode NFC normalization"""
        if not text:
            return ""
        normalized = unicodedata.normalize('NFC', text)
        normalized = ''.join(char for char in normalized if not unicodedata.category(char).startswith('C'))
        return normalized

    @staticmethod
    def clean_khmer_text(text: str) -> str:
        """Clean Khmer text by removing unwanted characters"""
        if not text:
            return ""
        text = TextProcessor.normalize_khmer_text(text)
        chars_to_remove = (Config.KHSYM | Config.KHNUMBER | Config.ARABIC_NUMBER | 
                          Config.LATIN_CHARS | Config.PUNCTUATION)
        translation_table = str.maketrans('', '', ''.join(chars_to_remove))
        text = text.translate(translation_table)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def normalize_word(word: str) -> str:
        """Normalize individual Khmer words"""
        if not word:
            return ""
        word = unicodedata.normalize('NFC', word)
        word = word.strip()
        word = ''.join(char for char in word if not unicodedata.category(char).startswith('C'))
        return word

    @staticmethod
    def segment_khmer_text(text: str) -> str:
        """Segment Khmer text using sentence-based approach for better flow"""
        try:
            import khmernltk
            
            # First, split into sentences using Khmer and common sentence delimiters
            sentence_delimiters = ['។', '.', '!', '?', '\n']
            sentences = []
            current_sentence = ""
            
            for char in text:
                current_sentence += char
                if char in sentence_delimiters:
                    if current_sentence.strip():
                        sentences.append(current_sentence.strip())
                    current_sentence = ""
            
            # Add remaining text as a sentence if any
            if current_sentence.strip():
                sentences.append(current_sentence.strip())
            
            # Process each sentence with word tokenization but keep sentence structure
            processed_sentences = []
            for sentence in sentences:
                if sentence:
                    # Clean the sentence first
                    cleaned_sentence = sentence.strip()
                    
                    # Use KhmerNLTK for word tokenization within the sentence
                    try:
                        word_tokens = khmernltk.word_tokenize(cleaned_sentence)
                        # Normalize each word but maintain sentence boundaries
                        normalized_words = []
                        for token in word_tokens:
                            normalized_token = TextProcessor.normalize_word(token)
                            if normalized_token and normalized_token not in sentence_delimiters:
                                normalized_words.append(normalized_token)
                        
                        if normalized_words:
                            # Rejoin words in the sentence with spaces
                            processed_sentence = ' '.join(normalized_words)
                            processed_sentences.append(processed_sentence)
                            
                    except Exception:
                        # Fallback: use the cleaned sentence as-is
                        if cleaned_sentence:
                            processed_sentences.append(cleaned_sentence)
            
            # Join sentences with sentence delimiters to maintain structure
            return ' ។ '.join(processed_sentences) if processed_sentences else text
            
        except Exception as e:
            logging.warning(f"Sentence-based segmentation failed: {e}")
            # Fallback to simple sentence splitting
            sentences = []
            for delimiter in ['។', '.', '!', '?']:
                if delimiter in text:
                    parts = text.split(delimiter)
                    for i, part in enumerate(parts[:-1]):  # Exclude last empty part
                        if part.strip():
                            sentences.append(part.strip())
            
            return ' ។ '.join(sentences) if sentences else text

class ModelManager:
    """Manage model loading and caching"""
    
    @staticmethod
    @st.cache_resource
    def load_models():
        """Load SVM model, FastText model, and configuration"""
        try:
            svm_model = joblib.load(Config.SVM_MODEL_PATH)
            with open(Config.CONFIG_PATH, "r") as f:
                config = json.load(f)
            from gensim.models.fasttext import load_facebook_model
            fasttext_model = load_facebook_model(config["model_path"])
            return svm_model, fasttext_model, config
        except Exception as e:
            st.error(f"Error loading models: {e}")
            st.stop()

class AnalyticsEngine:
    """Advanced analytics and visualization engine"""
    
    @staticmethod
    def get_text_statistics(text: str) -> Dict[str, Any]:
        """Comprehensive text statistics analysis"""
        words = text.split()
        chars = len(text)
        sentences = max(1, text.count('។') + text.count('.') + text.count('!') + text.count('?'))
        
        # Advanced metrics
        unique_words = len(set(words))
        avg_word_length = np.mean([len(word) for word in words]) if words else 0
        lexical_diversity = unique_words / len(words) if words else 0
        
        # Khmer-specific metrics
        khmer_chars = sum(1 for char in text if char in Config.KHCONST)
        khmer_ratio = khmer_chars / chars if chars > 0 else 0
        
        return {
            'characters': chars,
            'words': len(words),
            'unique_words': unique_words,
            'sentences': sentences,
            'avg_word_length': avg_word_length,
            'avg_sentence_length': len(words) / sentences,
            'lexical_diversity': lexical_diversity,
            'khmer_character_ratio': khmer_ratio,
            'readability_score': AnalyticsEngine._calculate_readability(words, sentences)
        }
    
    @staticmethod
    def _calculate_readability(words: List[str], sentences: int) -> float:
        """Calculate readability score (simplified Flesch-Kincaid adaptation)"""
        if not words or sentences == 0:
            return 0.0
        avg_sentence_length = len(words) / sentences
        avg_word_length = np.mean([len(word) for word in words])
        # Simplified readability score for Khmer text
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (avg_word_length / 10))
        return max(0, min(100, score))

class ClassificationEngine:
    """Advanced classification engine with confidence analysis"""
    
    def __init__(self, svm_model, fasttext_model, embedding_method: str = "mean"):
        self.svm_model = svm_model
        self.fasttext_model = fasttext_model
        self.embedding_method = embedding_method
    
    def get_sentence_embedding(self, segmented_text: str) -> np.ndarray:
        """Generate sentence embedding from segmented text"""
        words = segmented_text.strip().split()
        if not words:
            return np.zeros(300)
        
        word_vecs = []
        for word in words:
            try:
                if hasattr(self.fasttext_model, 'get_word_vector'):
                    vec = self.fasttext_model.get_word_vector(word)
                elif hasattr(self.fasttext_model, 'wv') and word in self.fasttext_model.wv:
                    vec = self.fasttext_model.wv[word]
                elif hasattr(self.fasttext_model, 'get_vector'):
                    vec = self.fasttext_model.get_vector(word)
                else:
                    vec = self.fasttext_model[word]
                word_vecs.append((word, vec))
            except Exception:
                continue
        
        if not word_vecs:
            return np.zeros(300)
        
        if self.embedding_method == "mean":
            return np.mean([vec for _, vec in word_vecs], axis=0)
        elif self.embedding_method == "weighted":
            word_counts = collections.Counter(word for word, _ in word_vecs)
            total_count = sum(word_counts.values())
            weighted_vecs = [vec * (word_counts[word]/total_count) for word, vec in word_vecs]
            return np.sum(weighted_vecs, axis=0)
        
        return np.mean([vec for _, vec in word_vecs], axis=0)
    
    def classify_text(self, text: str) -> ClassificationResult:
        """Perform comprehensive text classification"""
        start_time = time.time()
        
        # Generate unique prediction ID
        prediction_id = hashlib.md5(f"{text[:100]}{datetime.now()}".encode()).hexdigest()[:8]
        
        # Preprocess text
        cleaned = TextProcessor.clean_khmer_text(text)
        segmented = TextProcessor.segment_khmer_text(cleaned)
        
        # Get embedding
        embedding = self.get_sentence_embedding(segmented)
        embedding_reshaped = embedding.reshape(1, -1)
        
        # Get prediction and confidence scores
        prediction = self.svm_model.predict(embedding_reshaped)[0]
        
        # Calculate confidence scores
        confidence_dict = self._calculate_confidence_scores(embedding_reshaped)
        
        # Get text statistics
        text_stats = AnalyticsEngine.get_text_statistics(text)
        
        processing_time = time.time() - start_time
        
        return ClassificationResult(
            prediction=prediction,
            confidence=confidence_dict,
            processing_time=processing_time,
            cleaned_text=cleaned,
            segmented_text=segmented,
            embedding=embedding,
            timestamp=datetime.now(),
            input_text=text,  # Store complete original text
            text_statistics=text_stats,
            prediction_id=prediction_id
        )
    
    def _calculate_confidence_scores(self, embedding_reshaped: np.ndarray) -> Dict[str, float]:
        """Calculate confidence scores for all categories"""
        if hasattr(self.svm_model, 'decision_function'):
            decision_scores = self.svm_model.decision_function(embedding_reshaped)[0]
            # Convert to probabilities using softmax
            exp_scores = np.exp(decision_scores - np.max(decision_scores))
            probabilities = exp_scores / np.sum(exp_scores)
            
            confidence_dict = {}
            for i, category in enumerate(Config.CATEGORIES):
                confidence_dict[category] = probabilities[i] if i < len(probabilities) else 0.0
        else:
            # Fallback for models without decision_function
            pred = self.svm_model.predict(embedding_reshaped)[0]
            confidence_dict = {pred: 0.95}
            for cat in Config.CATEGORIES:
                if cat != pred:
                    confidence_dict[cat] = 0.05 / (len(Config.CATEGORIES) - 1)
        
        return confidence_dict

# Initialize database on startup
# DatabaseManager.init_database()

# Load models and data
svm_model, fasttext_model, config = ModelManager.load_models()
classification_engine = ClassificationEngine(svm_model, fasttext_model, config.get("embedding_method", "mean"))

# Initialize session state
if 'classification_history' not in st.session_state:
    st.session_state.classification_history = []
if 'model_performance' not in st.session_state:
    st.session_state.model_performance = {}
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {
        'theme': 'light',
        'language': 'en',
        'show_advanced': False
    }

def extract_pdf_text(pdf_file):
    """Extract text from uploaded PDF file and format into proper sentences and paragraphs"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        # Extract text from all pages
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:  # Only add non-empty text
                text += page_text + "\n"
        
        if not text.strip():
            return None
            
        # Clean and format the extracted text
        formatted_text = format_extracted_text(text)
        return formatted_text
        
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

def format_extracted_text(raw_text):
    """Format raw extracted text into proper sentences and paragraphs"""
    if not raw_text:
        return ""
    
    # Remove excessive whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', raw_text.strip())
    
    # Define sentence-ending punctuation for multiple languages
    sentence_endings = ['។', '.', '!', '?', ':', ';']
    paragraph_indicators = ['\n\n', '\n \n', '  \n']
    
    # Split into potential sentences
    sentences = []
    current_sentence = ""
    
    i = 0
    while i < len(text):
        char = text[i]
        current_sentence += char
        
        # Check for sentence endings
        if char in sentence_endings:
            # Look ahead to see if this is really the end of a sentence
            next_chars = text[i+1:i+3] if i+1 < len(text) else ""
            
            # If followed by whitespace and capital letter or Khmer character, it's likely a sentence end
            if (next_chars and 
                (next_chars[0].isspace() and 
                 (len(next_chars) > 1 and 
                  (next_chars[1].isupper() or 
                   next_chars[1] in Config.KHCONST or
                   next_chars[1].isdigit())))):
                
                # Clean up the sentence
                clean_sentence = current_sentence.strip()
                if clean_sentence and len(clean_sentence) > 3:  # Avoid very short fragments
                    sentences.append(clean_sentence)
                current_sentence = ""
        i += 1
    
    # Add any remaining text as a sentence
    if current_sentence.strip() and len(current_sentence.strip()) > 3:
        sentences.append(current_sentence.strip())
    
    # Group sentences into paragraphs
    if not sentences:
        return raw_text.strip()
    
    # Smart paragraph grouping
    paragraphs = []
    current_paragraph = []
    
    for sentence in sentences:
        current_paragraph.append(sentence)
        
        # Start new paragraph if:
        # 1. Current paragraph has 3+ sentences, or
        # 2. Sentence seems to be a title/header (short and ends with certain punctuation)
        # 3. Topic seems to change (basic heuristic)
        
        should_break = False
        
        # Check if we have enough sentences for a paragraph
        if len(current_paragraph) >= 4:
            should_break = True
        
        # Check if next sentence might be a new topic (if available)
        current_idx = sentences.index(sentence)
        if current_idx < len(sentences) - 1:
            next_sentence = sentences[current_idx + 1]
            
            # Simple heuristics for paragraph breaks
            if (len(sentence) < 50 and  # Short sentence
                (sentence.endswith(':') or sentence.endswith('។') or sentence.endswith('.'))):
                should_break = True
            
            # If current sentence is very long, consider it a paragraph by itself
            if len(sentence) > 300:
                should_break = True
        
        if should_break and current_paragraph:
            paragraph_text = ' '.join(current_paragraph)
            paragraphs.append(paragraph_text)
            current_paragraph = []
    
    # Add any remaining sentences as final paragraph
    if current_paragraph:
        paragraph_text = ' '.join(current_paragraph)
        paragraphs.append(paragraph_text)
    
    # Join paragraphs with double line breaks
    formatted_text = '\n\n'.join(paragraphs)
    
    # Final cleanup
    formatted_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', formatted_text)  # Remove excessive line breaks
    formatted_text = re.sub(r'[ \t]+', ' ', formatted_text)  # Normalize spaces
    
    return formatted_text.strip()

def export_results(result):
    """Export a single classification result to JSON"""
    export_data = {
        "prediction": result.prediction,
        "category_label": Config.CATEGORY_LABELS[result.prediction],
        "confidence": result.confidence[result.prediction],
        "all_confidences": result.confidence,
        "text": result.input_text,
        "processing_time": result.processing_time,
        "timestamp": result.timestamp.isoformat(),
        "prediction_id": result.prediction_id,
        "text_statistics": result.text_statistics
    }
    
    # Convert to JSON string
    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    # Use Streamlit download button
    st.download_button(
        label="📥 Download JSON",
        data=json_str,
        file_name=f"classification_{result.prediction_id}.json",
        mime="application/json",
        key=f"download_{result.prediction_id}"
    )
    
    st.success("Export ready! Click the download button above.")

def export_session_history(results):
    """Export multiple classification results to JSON"""
    export_data = []
    
    for result in results:
        export_data.append({
            "prediction": result.prediction,
            "category_label": Config.CATEGORY_LABELS[result.prediction],
            "confidence": max(result.confidence.values()),
            "all_confidences": result.confidence,
            "text": result.input_text,
            "processing_time": result.processing_time,
            "timestamp": result.timestamp.isoformat(),
            "prediction_id": result.prediction_id,
            "text_statistics": result.text_statistics
        })
    
    # Convert to JSON string
    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    # Use Streamlit download button
    st.download_button(
        label="📥 Download All Results",
        data=json_str,
        file_name=f"classification_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        key="download_all_results"
    )
    
    st.success(f"Export ready! {len(results)} records included.")
    
# Initialize database on startup
# DatabaseManager.init_database() - Commented out as database functionality removed

def render_single_analysis():
    """Side-by-side input and output layout"""
    
    # Create two main columns - Input on left, Output on right
    input_col, output_col = st.columns([1, 1], gap="large")
    
    with input_col:
    
        
        # Input method selection with modern tab-based approach
        st.markdown("### Input Selection")
        
        # Create interactive tabs for input methods
        input_tab1, input_tab2 = st.tabs(["**Text Input**", "**PDF Upload**"])
        
        text_input = ""
        
        with input_tab1:
            st.markdown("#### Direct Text Entry")
            st.markdown("*Perfect for quick analysis of copied articles or short texts*")
            
            text_input = st.text_area(
                "Paste your Khmer news article here:",
                height=350,
                placeholder="បញ្ចូលអត្ថបទភាសាខ្មែរនៅទីនេះ...\n\nExample:\nរដ្ឋាភិបាលកម្ពុជាបានប្រកាសគម្រោងអភិវឌ្ឍន៍ថ្មីសម្រាប់កម្មវិធីបរិស្ថាន និងការកាត់បន្ថយការប្រើប្រាស់ភ្លាស្ទិក...",
                help="Tip: For best results, use complete sentences with at least 50 words"
            )
            
            if text_input:
                # Live text analysis panel
                st.markdown("##### Live Text Analysis")
                
                # Create metrics in a 2x2 grid
                metric_col1, metric_col2 = st.columns(2)
                
                with metric_col1:
                    char_count = len(text_input)
                    word_count = len(text_input.split())
                    st.metric("Characters", f"{char_count:,}", 
                             delta=f"+{char_count}" if char_count > 0 else None)
                    st.metric("Words", f"{word_count:,}",
                             delta=f"+{word_count}" if word_count > 0 else None)
                
                with metric_col2:
                    sentences = max(1, text_input.count('។') + text_input.count('.') + 
                                  text_input.count('!') + text_input.count('?'))
                    khmer_chars = sum(1 for char in text_input if char in Config.KHCONST)
                    khmer_ratio = khmer_chars / len(text_input) if len(text_input) > 0 else 0
                    
                    st.metric("Sentences", f"{sentences:,}")
                    st.metric("Khmer Content", f"{khmer_ratio:.1%}",
                             delta="Good" if khmer_ratio > 0.8 else "Check content" if khmer_ratio > 0.5 else "Low Khmer")
                
                # Text quality indicator
                if word_count >= 50:
                    st.success("Text length is optimal for classification")
                elif word_count >= 20:
                    st.warning("Text is short but analyzable")
                else:
                    st.info("Consider adding more text for better accuracy")
        
        with input_tab2:
            st.markdown("#### PDF Document Upload")
            st.markdown("*Ideal for analyzing longer articles, research papers, or saved documents*")
            
            # Create an upload area with custom styling
            uploaded_file = st.file_uploader(
                "Choose your PDF file",
                type=["pdf"],
                help="Upload PDF files containing Khmer text. Maximum file size: 10MB",
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                # File info display
                file_size = len(uploaded_file.getvalue()) / 1024  # KB
                st.info(f"**{uploaded_file.name}** ({file_size:.1f} KB)")
                
                # Progress bar for extraction
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("Extracting text from PDF...")
                    progress_bar.progress(25)
                    
                    extracted_text = extract_pdf_text(uploaded_file)
                    progress_bar.progress(75)
                    
                    if extracted_text:
                        text_input = extracted_text
                        progress_bar.progress(100)
                        status_text.empty()
                        progress_bar.empty()
                        
                        # Success notification                        st.success(f"Successfully extracted {len(extracted_text):,} characters!")
                        
                        # PDF analysis results
                        st.markdown("##### Document Analysis")
                        
                        # Create metrics layout
                        pdf_col1, pdf_col2, pdf_col3 = st.columns(3)
                        
                        with pdf_col1:
                            st.metric("File Size", f"{file_size:.1f} KB")
                        
                        with pdf_col2:
                            word_count = len(extracted_text.split())
                            st.metric("Words", f"{word_count:,}")
                        
                        with pdf_col3:
                            st.metric("Characters", f"{len(extracted_text):,}")
                        
                        # Document preview with enhanced display
                        with st.expander("📖 Document Preview", expanded=False):
                            # Toggle for showing complete document
                            show_complete = st.toggle("Show Complete Document")
                            
                            if show_complete:
                                # Show complete document in the same field
                                st.markdown("**Complete Document Content:**")
                                st.text_area(
                                    "Full Document:",
                                    extracted_text,
                                    height=500,
                                    disabled=True,
                                    key="pdf_complete"
                                )
                            else:
                                # Show preview only
                                preview_length = min(1000, len(extracted_text))
                                preview_text = extracted_text[:preview_length]
                                if len(extracted_text) > preview_length:
                                    preview_text += "\n\n... [Document continues - toggle above to see complete text]"
                                
                                st.markdown("**First 1000 characters:**")
                                st.text_area(
                                    "Document Preview:",
                                    preview_text,
                                    height=500,
                                    disabled=True,
                                    key="pdf_preview"
                                )
                            
                            # Popup button for extracted text
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                # Copy to clipboard button
                                if st.button("Copy Text", type="secondary", use_container_width=True):
                                    st.code(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
                                    st.success("Text ready to copy!")
                            
                            with col2:
                                # Download button
                                st.download_button(
                                    label="Download TXT",
                                    data=extracted_text,
                                    file_name=f"extracted_{uploaded_file.name}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                    else:
                        progress_bar.empty()
                        status_text.empty()
                        st.error("Failed to extract text from PDF. Please ensure the file contains readable text.")
                        
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"Error processing PDF: {str(e)}")
            
            else:
                # Show upload instructions when no file is selected
                st.markdown("""
                <div style="
                    border: 2px dashed #cccccc;
                    border-radius: 10px;
                    padding: 2rem;
                    text-align: center;
                    background-color: #f9f9f9;
                    margin: 1rem 0;
                ">
                    <h4 style="color: #666;">Upload Instructions</h4>
                    <p style="color: #888; margin: 0.5rem 0;">
                        • Supported format: PDF files only<br>
                        • Maximum file size: 10MB<br>
                        • Best for: Multi-page documents, articles, reports
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # Analysis button
        st.markdown("---")
        if text_input:
            if st.button("Analyze Text", type="primary", use_container_width=True):
                # Store result in session state to display in output column
                with st.spinner("Analyzing..."):
                    result = classification_engine.classify_text(text_input)
                    st.session_state.classification_history.append(result)
                    st.session_state.current_result = result
                    
                    # Save to database
                    # DatabaseManager.save_classification(result)
                    
                st.success("Analysis complete! Check results on the right")
    
    with output_col:
        st.markdown("### Results Section")
        
        if 'current_result' in st.session_state:
            result = st.session_state.current_result
            
            # Main prediction card (clickable) with confidence
            predicted_category = Config.CATEGORY_LABELS[result.prediction]
            confidence = result.confidence[result.prediction]
            
            # Create enhanced clickable prediction card with HTML wrapper
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                padding: 1.5rem 2rem;
                border-radius: 15px;
                color: white;
                text-align: center;
                margin: 1rem 0;
                box-shadow: 0 4px 15px rgba(40,167,69,0.3);
                cursor: pointer;
                transition: all 0.3s ease;
                border: none;
                position: relative;
                overflow: hidden;
            " onclick="
                if (!window.pipelineShown) {{
                    window.pipelineShown = true;
                    document.dispatchEvent(new CustomEvent('showPipeline'));
                }}
            ">
                <div style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: linear-gradient(45deg, rgba(255,255,255,0.1) 25%, transparent 25%), 
                                linear-gradient(-45deg, rgba(255,255,255,0.1) 25%, transparent 25%);
                    background-size: 20px 20px;
                    opacity: 0.3;
                "></div>
                <div style="position: relative; z-index: 1;">
                    <h3 style="margin: 0; font-size: 1.3rem; font-weight: 700; margin-bottom: 0.3rem;">
                        📂 {predicted_category}
                    </h3>
                    <p style="margin: 0; font-size: 1.1rem; font-weight: 600; opacity: 0.95;">
                        Confidence: {confidence:.1%}
                    </p>
                </div>
            </div>
            
            <script>
                document.addEventListener('showPipeline', function() {{
                    window.parent.postMessage({{type: 'showPipeline'}}, '*');
                }});
            </script>
            """, unsafe_allow_html=True)
            
            # Check for pipeline display request
            if 'show_pipeline_request' not in st.session_state:
                st.session_state.show_pipeline_request = False
            
            # Wide button to trigger pipeline
            if st.button("Show Preprocessing Pipeline", key="pipeline_trigger", type="primary", use_container_width=True):
                st.session_state.show_pipeline = True
                try:
                    st.experimental_rerun()
                except:
                    st.session_state["refresh_required"] = True
                    pass
            
            # Show pipeline inline if requested
            if st.session_state.get('show_pipeline', False):
                st.markdown("---")
                st.markdown("### Preprocessing Pipeline")
                
                # Create tabs for each pipeline step
                tab1, tab2, tab3 = st.tabs(["1. Original", "2. Cleaned", "3. Segmented"])
                
                with tab1:
                    st.markdown("**Raw input as received**")
                    st.text_area(
                        "Original Text:",
                        result.input_text,
                        height=300,
                        disabled=True,
                        key="pipeline_tab_original"
                    )
                
                with tab2:
                    st.markdown("**Normalized & symbols removed**")
                    st.text_area(
                        "Cleaned Text:",
                        result.cleaned_text,
                        height=300,
                        disabled=True,
                        key="pipeline_tab_cleaned"
                    )
                
                with tab3:
                    st.markdown("**Word tokenized & sentence structured**")
                    st.text_area(
                        "Segmented Text:",
                        result.segmented_text,
                        height=300,
                        disabled=True,
                        key="pipeline_tab_segmented"
                    )
                
                # Close button for pipeline
                if st.button("Hide Pipeline", type="secondary", use_container_width=True):
                    st.session_state.show_pipeline = False
                    try:
                        st.experimental_rerun()
                    except:
                        st.session_state["refresh_required"] = True
                        pass
                
                st.markdown("---")
            
            # Quick metrics
            stats = result.text_statistics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Time", f"{result.processing_time:.3f}s")
            with col2:
                st.metric("Words", f"{stats['words']:,}")
            
            # Confidence breakdown
            st.markdown("### Confidence Scores")
            confidence_data = sorted(result.confidence.items(), key=lambda x: x[1], reverse=True)
            
            for i, (cat, conf) in enumerate(confidence_data):
                color = "#28a745" if i == 0 else "#ffc107" if conf > 0.1 else "#6c757d"
                bar_width = conf * 100
                
                st.markdown(f"""
                <div style="margin: 0.5rem 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.2rem;">
                        <span style="font-weight: 500; font-size: 0.9rem;">{Config.CATEGORY_LABELS[cat]}</span>
                        <span style="color: {color}; font-weight: bold;">{conf:.1%}</span>
                    </div>
                    <div style="background-color: #e9ecef; height: 15px; border-radius: 8px; overflow: hidden;">
                        <div style="background-color: {color}; height: 100%; width: {bar_width}%; transition: width 0.3s ease;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Action buttons
            st.markdown("#### Actions")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Export", type="secondary", use_container_width=True):
                    export_results(result)
            with col2:
                if st.button("Clear", type="secondary", use_container_width=True):
                    if 'current_result' in st.session_state:
                        del st.session_state.current_result
                    st.session_state["refresh_required"] = True
                    # Use newer Streamlit APIs in safer way
                    try:
                        st.experimental_rerun()
                    except:
                        pass
        
        else:
            st.markdown("""
            <div class="info-box">
                <h4>👈 Enter text on the left</h4>
                <p>Results will appear here after you:</p>
                <ul>
                    <li>Enter Khmer text or upload PDF</li>
                    <li>Click the "Analyze Text" button</li>
                </ul>
                <p><em>The analysis will show classification results, confidence scores, and detailed analytics.</em></p>
            </div>
            """, unsafe_allow_html=True)

def render_session_history():
    """Render the session history page showing all classified articles with improved UI"""
    
    if not st.session_state.classification_history:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 3rem 2rem;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            border: 2px dashed #dee2e6;
            margin: 2rem 0;
        ">
            <h2 style="color: #6c757d; margin-bottom: 1rem;">No Articles Yet</h2>
            <p style="color: #868e96; font-size: 1.1rem; margin-bottom: 1.5rem;">
                Your classified articles will appear here after analysis
            </p>
            <p style="color: #adb5bd; font-style: italic;">
                Start by entering Khmer text or uploading a PDF in the Classifier tab
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Enhanced header with statistics
    total_articles = len(st.session_state.classification_history)
    categories_used = len(set(result.prediction for result in st.session_state.classification_history))
    avg_confidence = np.mean([max(result.confidence.values()) for result in st.session_state.classification_history])
    
    st.markdown("### Session Overview")
    
    # Statistics cards in a responsive grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <h3 style="margin: 0; font-size: 2rem;">{total_articles}</h3>
            <p style="margin: 0; opacity: 0.9;">Total Articles</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h3 style="margin: 0; font-size: 2rem;">{categories_used}/6</h3>
            <p style="margin: 0; opacity: 0.9;">Categories Used</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h3 style="margin: 0; font-size: 2rem;">{avg_confidence:.0%}</h3>
            <p style="margin: 0; opacity: 0.9;">Avg Confidence</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Most frequent category
        category_counts = {}
        for result in st.session_state.classification_history:
            cat = result.prediction
            category_counts[cat] = category_counts.get(cat, 0) + 1
        most_common_cat = max(category_counts.items(), key=lambda x: x[1]) if category_counts else ("N/A", 0)
        
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <h3 style="margin: 0; font-size: 1.2rem;">{Config.CATEGORY_LABELS.get(most_common_cat[0], "N/A")}</h3>
            <p style="margin: 0; opacity: 0.9;">Top Category</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Category distribution visualization
    st.markdown("---")
    st.markdown("### Category Distribution")
    
    if category_counts:
        # Create a more visual category distribution
        cats_per_row = 3
        category_items = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        for i in range(0, len(category_items), cats_per_row):
            cols = st.columns(cats_per_row)
            for j, (cat, count) in enumerate(category_items[i:i+cats_per_row]):
                with cols[j]:
                    percentage = (count / total_articles) * 100
                    bar_width = percentage
                    
                    st.markdown(f"""
                    <div style="
                        background: white;
                        padding: 1.5rem;
                        border-radius: 12px;
                        border-left: 5px solid #28a745;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        margin: 0.5rem 0;
                        transition: transform 0.2s ease;
                    " onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
                        <h4 style="margin: 0 0 0.5rem 0; color: #2c3e50;">{Config.CATEGORY_LABELS[cat]}</h4>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.5rem; font-weight: bold; color: #28a745;">{count}</span>
                            <span style="color: #6c757d; font-size: 0.9rem;">{percentage:.1f}%</span>
                        </div>
                        <div style="background-color: #e9ecef; height: 8px; border-radius: 4px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #28a745, #20c997); height: 100%; width: {bar_width}%; transition: width 0.3s ease;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Enhanced search and filter options
    st.markdown("### Advanced Filters")
    
    # Filter controls in columns
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 1, 1, 1])
    
    with filter_col1:
        search_query = st.text_input(
            "Search articles...", 
            placeholder="Search by content, keywords, or phrases...",
            help="Search within article text content"
        )
    
    with filter_col2:
        category_filter = st.selectbox(
            "Category:",
            ["All Categories"] + [Config.CATEGORY_LABELS[cat] for cat in Config.CATEGORIES],
            help="Filter by news category"
        )
    
    with filter_col3:
        confidence_filter = st.selectbox(
            "Confidence:",
            ["All Levels", "High (>80%)", "Medium (50-80%)", "Low (<50%)"],
            help="Filter by prediction confidence"
        )
    
    with filter_col4:
        sort_option = st.selectbox(
            "📅 Sort by:",
            ["Most Recent", "Oldest First", "Highest Confidence", "Lowest Confidence", "A-Z Category"],
            help="Choose sorting method"
        )
    
    # Apply filters
    filtered_results = st.session_state.classification_history.copy()
    
    # Category filter
    if category_filter != "All Categories":
        selected_cat = next(cat for cat, label in Config.CATEGORY_LABELS.items() if label == category_filter)
        filtered_results = [r for r in filtered_results if r.prediction == selected_cat]
    
    # Search filter
    if search_query:
        search_lower = search_query.lower()
        filtered_results = [
            r for r in filtered_results 
            if search_lower in r.input_text.lower()
        ]
    
    # Confidence filter
    if confidence_filter != "All Levels":
        if confidence_filter == "High (>80%)":
            filtered_results = [r for r in filtered_results if max(r.confidence.values()) > 0.8]
        elif confidence_filter == "Medium (50-80%)":
            filtered_results = [r for r in filtered_results if 0.5 <= max(r.confidence.values()) <= 0.8]
        elif confidence_filter == "Low (<50%)":
            filtered_results = [r for r in filtered_results if max(r.confidence.values()) < 0.5]
    
    # Apply sorting
    if sort_option == "Most Recent":
        filtered_results = sorted(filtered_results, key=lambda x: x.timestamp, reverse=True)
    elif sort_option == "Oldest First":
        filtered_results = sorted(filtered_results, key=lambda x: x.timestamp)
    elif sort_option == "Highest Confidence":
        filtered_results = sorted(filtered_results, key=lambda x: max(x.confidence.values()), reverse=True)
    elif sort_option == "Lowest Confidence":
        filtered_results = sorted(filtered_results, key=lambda x: max(x.confidence.values()))
    elif sort_option == "A-Z Category":
        filtered_results = sorted(filtered_results, key=lambda x: Config.CATEGORY_LABELS[x.prediction])
    
    # Results header with count
    st.markdown(f"### Articles ({len(filtered_results)} found)")
    
    if not filtered_results:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 2rem;
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            margin: 1rem 0;
        ">
            <h4 style="color: #856404;">No Results Found</h4>
            <p style="color: #856404; margin: 0;">
                Try adjusting your search criteria or filters
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Action buttons
    action_col1, action_col2, action_col3 = st.columns([1, 1, 2])
    
    with action_col1:
        if st.button("Export All", type="primary", use_container_width=True):
            export_session_history(filtered_results)
    
    with action_col2:
        if st.button("Clear History", type="secondary", use_container_width=True):
            if st.session_state.get('confirm_clear', False):
                st.session_state.classification_history = []
                st.session_state.confirm_clear = False
                try:
                    st.experimental_rerun()
                except:
                    st.session_state["refresh_required"] = True
                    pass
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm clearing all history")
    
    with action_col3:
        # Display showing results info
        st.markdown(f"<p style='text-align: right; color: #6c757d; margin-top: 0.5rem;'>Showing {len(filtered_results)} of {total_articles} articles</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Enhanced article cards
    for i, result in enumerate(filtered_results):
        confidence_pct = max(result.confidence.values())
        confidence_color = "#28a745" if confidence_pct > 0.8 else "#ffc107" if confidence_pct > 0.5 else "#dc3545"
        
        # Create a more attractive expandable card
        with st.expander(
            f"{Config.CATEGORY_LABELS[result.prediction]} • {result.timestamp.strftime('%m/%d %H:%M')} • {confidence_pct:.0%} confidence",
            expanded=False
        ):
            # Enhanced layout with better visual hierarchy
            main_col, sidebar_col = st.columns([2.5, 1])
            
            with main_col:
                # Article content section
                st.markdown("#### Article Content")
                
                # Smart preview with better formatting
                preview_length = 300
                preview_text = result.input_text[:preview_length]
                if len(result.input_text) > preview_length:
                    preview_text += "..."
                
                st.markdown(f"""
                <div style="
                    background-color: #f8f9fa;
                    padding: 1rem;
                    border-radius: 8px;
                    border-left: 4px solid {confidence_color};
                    margin: 1rem 0;
                ">
                    <p style="margin: 0; line-height: 1.6; color: #2c3e50;">
                        {preview_text}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Full text toggle
                if len(result.input_text) > preview_length:
                    show_full = st.toggle(f"📖 Show Complete Text", key=f"full_{result.prediction_id}")
                    if show_full:
                        st.text_area(
                            "Complete Article:",
                            result.input_text,
                            height=250,
                            disabled=True,
                            key=f"full_text_{result.prediction_id}"
                        )
            
            with sidebar_col:
                # Metrics and info panel
                st.markdown("#### Article Metrics")
                
                # Category with color coding
                st.markdown(f"""
                <div style="
                    background: {confidence_color};
                    color: white;
                    padding: 0.8rem;
                    border-radius: 8px;
                    text-align: center;
                    margin-bottom: 1rem;
                ">
                    <h4 style="margin: 0; font-size: 1.1rem;">{Config.CATEGORY_LABELS[result.prediction]}</h4>
                    <p style="margin: 0; opacity: 0.9;">Confidence: {confidence_pct:.1%}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Detailed metrics
                st.metric("Processing Time", f"{result.processing_time:.3f}s")
                st.metric("Word Count", f"{result.text_statistics['words']:,}")
                st.metric("Characters", f"{result.text_statistics['characters']:,}")
                st.metric("Sentences", f"{result.text_statistics['sentences']:,}")
                
                # Quick actions
                st.markdown("#### Quick Actions")
                
                if st.button(f"Re-analyze", key=f"reanalyze_{result.prediction_id}", use_container_width=True, type="secondary"):
                    with st.spinner("Re-analyzing..."):
                        new_result = classification_engine.classify_text(result.input_text)
                        st.session_state.classification_history.append(new_result)
                        st.session_state.current_result = new_result
                    st.success("Re-analyzed! Check results in Classifier tab.")
                
                # Export individual result
                export_data = {
                    "prediction": result.prediction,
                    "category_label": Config.CATEGORY_LABELS[result.prediction],
                    "confidence": max(result.confidence.values()),
                    "all_confidences": result.confidence,
                    "text": result.input_text,
                    "processing_time": result.processing_time,
                    "timestamp": result.timestamp.isoformat(),
                    "prediction_id": result.prediction_id,
                    "text_statistics": result.text_statistics
                }
                
                json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="Export JSON",
                    data=json_str,
                    file_name=f"article_{result.prediction_id}.json",
                    mime="application/json",
                    key=f"export_{result.prediction_id}",
                    use_container_width=True,
                    type="secondary"
                )
            
            # Enhanced confidence breakdown
            st.markdown("---")
            st.markdown("#### Detailed Confidence Analysis")
            
            confidence_data = sorted(result.confidence.items(), key=lambda x: x[1], reverse=True)
            
            # Create a grid for confidence scores
            conf_cols = st.columns(2)
            for idx, (cat, conf) in enumerate(confidence_data):
                col_idx = idx % 2
                with conf_cols[col_idx]:
                    is_predicted = cat == result.prediction
                    bar_color = "#28a745" if is_predicted else "#ffc107" if conf > 0.1 else "#6c757d"
                    
                    st.markdown(f"""
                    <div style="
                        background: white;
                        padding: 0.8rem;
                        border-radius: 8px;
                        border: 2px solid {'#28a745' if is_predicted else '#e9ecef'};
                        margin: 0.3rem 0;
                        box-shadow: {'0 2px 8px rgba(40,167,69,0.2)' if is_predicted else '0 1px 3px rgba(0,0,0,0.1)'};
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-weight: {'bold' if is_predicted else 'normal'}; font-size: 0.9rem; color: #2c3e50;">
                                {Config.CATEGORY_LABELS[cat]}
                            </span>
                            <span style="color: {bar_color}; font-weight: bold; font-size: 0.9rem;">{conf:.1%}</span>
                        </div>
                        <div style="background-color: #e9ecef; height: 6px; border-radius: 3px; overflow: hidden;">
                            <div style="background-color: {bar_color}; height: 100%; width: {conf * 100}%; transition: width 0.3s ease;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

def main():
    """Main application entry point with responsive UI layout"""
    # Header with application title and description
    st.markdown("<h1 class='main-header'>Multi-Class Khmer News Classifier</h1>", unsafe_allow_html=True)

    # Create tabs for different sections
    classifier_tab, session_history_tab = st.tabs([
        "**Classifier**", 
        "**Session History**"
    ])
    
    # Load the appropriate view based on selected tab
    with classifier_tab:
        render_single_analysis()
    
    with session_history_tab:
        render_session_history()
    
    # Footer
    st.markdown("---")
    st.markdown("Developed by Vengkim Seng & Darapong Rith | Multi-Class Khmer News Article Classification ", unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    main()