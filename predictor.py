"""
Spam Prediction Wrapper
Loads existing model and makes predictions
"""

import pickle
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk
import os
import config


class SpamPredictor:
    """Wrapper for spam prediction using trained model"""

    def get_model_and_vectorizer(self):
        """
        Get model and vectorizer for explainability
        
        Returns:
            tuple: (model, vectorizer)
        """
        return self.model, self.vectorizer
    
    def __init__(self):
        """Initialize predictor and load model"""
        self.model = None
        self.vectorizer = None
        self.stemmer = PorterStemmer()
        
        # Download NLTK data FIRST - FIXED VERSION
        self._ensure_nltk_data()
        
        # Then load stopwords
        self.stop_words = set(stopwords.words('english'))
        
        # Load model
        self.load_model()
    
    def _ensure_nltk_data(self):
        """Ensure NLTK data is downloaded - PRODUCTION FIX"""
        import ssl
        
        # Fix SSL certificate issues on cloud
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        
        # Download required NLTK data with error handling
        required_data = {
            'stopwords': 'corpora/stopwords',
            'punkt': 'tokenizers/punkt'
        }
        
        for name, path in required_data.items():
            try:
                nltk.data.find(path)
                print(f"✓ {name} already downloaded")
            except LookupError:
                print(f"Downloading {name}...")
                try:
                    nltk.download(name, quiet=False)
                    print(f"✓ {name} downloaded successfully")
                except Exception as e:
                    print(f"✗ Error downloading {name}: {e}")
                    # Try alternative download path
                    try:
                        nltk.download(name, download_dir=os.path.expanduser('~/nltk_data'))
                        print(f"✓ {name} downloaded to ~/nltk_data")
                    except Exception as e2:
                        print(f"✗ Failed to download {name}: {e2}")
    
    def load_model(self):
        """Load trained model and vectorizer"""
        try:
            if not os.path.exists(config.MODEL_FILE):
                raise FileNotFoundError(f"Model not found at {config.MODEL_FILE}")
            
            if not os.path.exists(config.VECTORIZER_FILE):
                raise FileNotFoundError(f"Vectorizer not found at {config.VECTORIZER_FILE}")
            
            with open(config.MODEL_FILE, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(config.VECTORIZER_FILE, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            return True, "Model loaded successfully"
            
        except Exception as e:
            return False, f"Error loading model: {str(e)}"
    
    def preprocess_text(self, text):
        """
        Preprocess text for prediction (same as training)
        
        Args:
            text (str): Input text
            
        Returns:
            str: Preprocessed text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize and remove stopwords
        words = text.split()
        words = [word for word in words if word not in self.stop_words]
        
        # Stem words
        words = [self.stemmer.stem(word) for word in words]
        
        return ' '.join(words)
    
    def predict(self, text):
        """
        Predict if text is spam or ham
        
        Args:
            text (str): Input text
            
        Returns:
            tuple: (prediction, confidence)
        """
        if not self.model or not self.vectorizer:
            return None, 0.0
        
        try:
            # Preprocess
            processed_text = self.preprocess_text(text)
            
            if not processed_text:
                # Empty text after preprocessing
                return 'ham', 50.0
            
            # Vectorize
            text_tfidf = self.vectorizer.transform([processed_text])
            
            # Predict
            prediction = self.model.predict(text_tfidf)[0]
            probabilities = self.model.predict_proba(text_tfidf)[0]
            
            # Get confidence
            if prediction == 'spam':
                confidence = probabilities[1] * 100
            else:
                confidence = probabilities[0] * 100
            
            return prediction, confidence
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return None, 0.0
    
    def predict_batch(self, texts):
        """
        Predict multiple texts at once
        
        Args:
            texts (list): List of text strings
            
        Returns:
            list: List of (prediction, confidence) tuples
        """
        results = []
        for text in texts:
            pred, conf = self.predict(text)
            results.append((pred, conf))
        return results
    
    def is_loaded(self):
        """Check if model is loaded"""
        return self.model is not None and self.vectorizer is not None