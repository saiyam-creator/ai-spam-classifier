"""
Spam Email Classifier - Training Script
This script trains a Naive Bayes classifier on spam/ham email data
"""

import pandas as pd
import numpy as np
import pickle
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import matplotlib.pyplot as plt
import seaborn as sns

# Download required NLTK data
print("Downloading NLTK resources...")
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

class SpamClassifier:
    """
    A spam email classifier using Naive Bayes algorithm
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=3000)
        self.model = MultinomialNB()
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text):
        """
        Preprocess the input text by:
        1. Converting to lowercase
        2. Removing special characters and numbers
        3. Removing stopwords
        4. Stemming words
        
        Args:
            text (str): Input text to preprocess
            
        Returns:
            str: Preprocessed text
        """
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
    
    def load_data(self, filepath):
        """
        Load and preprocess the dataset
        
        Args:
            filepath (str): Path to the CSV file
            
        Returns:
            tuple: Preprocessed messages and labels
        """
        print(f"Loading data from {filepath}...")
        
        # Read the CSV file
        df = pd.read_csv(filepath, encoding='latin-1')
        
        # Check column names and rename if necessary
        if 'v1' in df.columns and 'v2' in df.columns:
            df.columns = ['label', 'message'] + list(df.columns[2:])
        
        # Keep only necessary columns
        df = df[['label', 'message']]
        
        # Remove duplicates
        df.drop_duplicates(inplace=True)
        
        # Remove any null values
        df.dropna(inplace=True)
        
        print(f"Dataset shape: {df.shape}")
        print(f"Class distribution:\n{df['label'].value_counts()}")
        
        # Preprocess all messages
        print("Preprocessing text data...")
        df['processed_message'] = df['message'].apply(self.preprocess_text)
        
        return df['processed_message'], df['label']
    
    def train(self, X, y):
        """
        Train the spam classifier
        
        Args:
            X: Training messages
            y: Training labels
        """
        print("\nTraining the model...")
        
        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Transform text to TF-IDF features
        print("Vectorizing text data...")
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)
        
        # Train the Naive Bayes model
        print("Training Naive Bayes classifier...")
        self.model.fit(X_train_tfidf, y_train)
        
        # Make predictions
        y_train_pred = self.model.predict(X_train_tfidf)
        y_test_pred = self.model.predict(X_test_tfidf)
        
        # Calculate metrics
        train_accuracy = accuracy_score(y_train, y_train_pred)
        test_accuracy = accuracy_score(y_test, y_test_pred)
        
        print(f"\n{'='*50}")
        print("MODEL PERFORMANCE")
        print(f"{'='*50}")
        print(f"Training Accuracy: {train_accuracy*100:.2f}%")
        print(f"Testing Accuracy: {test_accuracy*100:.2f}%")
        
        # Classification report
        print(f"\n{'='*50}")
        print("CLASSIFICATION REPORT")
        print(f"{'='*50}")
        print(classification_report(y_test, y_test_pred))
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_test_pred)
        print(f"\n{'='*50}")
        print("CONFUSION MATRIX")
        print(f"{'='*50}")
        print(cm)
        
        # Plot confusion matrix
        self.plot_confusion_matrix(cm, ['ham', 'spam'])
        
        return test_accuracy
    
    def plot_confusion_matrix(self, cm, classes):
        """
        Plot confusion matrix as a heatmap
        
        Args:
            cm: Confusion matrix
            classes: List of class names
        """
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=classes, yticklabels=classes)
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig('models/confusion_matrix.png', dpi=300, bbox_inches='tight')
        print("\nConfusion matrix saved to 'models/confusion_matrix.png'")
        plt.close()
    
    def predict(self, text):
        """
        Predict whether a message is spam or ham
        
        Args:
            text (str): Input message
            
        Returns:
            tuple: (prediction, probability)
        """
        # Preprocess the text
        processed_text = self.preprocess_text(text)
        
        # Transform to TF-IDF
        text_tfidf = self.vectorizer.transform([processed_text])
        
        # Predict
        prediction = self.model.predict(text_tfidf)[0]
        probability = self.model.predict_proba(text_tfidf)[0]
        
        return prediction, probability
    
    def save_model(self, vectorizer_path='models/vectorizer.pkl', 
                   model_path='models/model.pkl'):
        """
        Save the trained model and vectorizer
        
        Args:
            vectorizer_path (str): Path to save the vectorizer
            model_path (str): Path to save the model
        """
        print(f"\nSaving model to '{model_path}'...")
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        print(f"Saving vectorizer to '{vectorizer_path}'...")
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        print("Model and vectorizer saved successfully!")
    
    def load_model(self, vectorizer_path='models/vectorizer.pkl', 
                   model_path='models/model.pkl'):
        """
        Load a pre-trained model and vectorizer
        
        Args:
            vectorizer_path (str): Path to the vectorizer file
            model_path (str): Path to the model file
        """
        print(f"Loading model from '{model_path}'...")
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        print(f"Loading vectorizer from '{vectorizer_path}'...")
        with open(vectorizer_path, 'rb') as f:
            self.vectorizer = pickle.load(f)
        
        print("Model and vectorizer loaded successfully!")


def main():
    """
    Main function to train the spam classifier
    """
    # Initialize classifier
    classifier = SpamClassifier()
    
    # Load data
    try:
        X, y = classifier.load_data('data/spam.csv')
    except FileNotFoundError:
        print("\nError: 'data/spam.csv' not found!")
        print("Please download the dataset from:")
        print("https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset")
        print("Or create a CSV file with 'label' and 'message' columns")
        return
    
    # Train the model
    accuracy = classifier.train(X, y)
    
    # Save the model
    classifier.save_model()
    
    # Test with example messages
    print(f"\n{'='*50}")
    print("TESTING WITH EXAMPLE MESSAGES")
    print(f"{'='*50}")
    
    test_messages = [
        "Congratulations! You've won a $1000 gift card. Click here to claim now!",
        "Hey, are we still meeting for lunch tomorrow?",
        "URGENT: Your account will be suspended. Verify your identity immediately!",
        "Can you pick up some milk on your way home?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        prediction, probability = classifier.predict(message)
        spam_prob = probability[1] if prediction == 'spam' else probability[0]
        print(f"\nMessage {i}: {message[:60]}...")
        print(f"Prediction: {prediction.upper()}")
        print(f"Confidence: {max(probability)*100:.2f}%")


if __name__ == "__main__":
    main()