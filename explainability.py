"""
ML Model Explainability Module
Explains why an email was classified as spam
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class SpamExplainer:
    """Explains spam classification decisions"""
    
    def __init__(self, model, vectorizer):
        """
        Initialize explainer with trained model and vectorizer
        
        Args:
            model: Trained Naive Bayes model
            vectorizer: Fitted TfidfVectorizer
        """
        self.model = model
        self.vectorizer = vectorizer
        self.feature_names = vectorizer.get_feature_names_out()
    
    def explain_prediction(self, text, prediction, confidence):
        """
        Generate explanation for spam prediction
        
        Args:
            text (str): Original email text
            prediction (str): 'spam' or 'ham'
            confidence (float): Prediction confidence
            
        Returns:
            dict: Explanation details
        """
        # Get TF-IDF features
        tfidf_vector = self.vectorizer.transform([text])
        
        # Get top contributing features
        top_features = self._get_top_features(tfidf_vector, prediction, n=10)
        
        # Generate human explanation
        explanation = self._generate_explanation(prediction, confidence, top_features)
        
        # Extract suspicious keywords
        suspicious_words = [feat['word'] for feat in top_features[:5]]
        
        return {
            'explanation': explanation,
            'top_features': top_features,
            'suspicious_words': suspicious_words,
            'confidence_reasoning': self._explain_confidence(confidence)
        }
    
    def _get_top_features(self, tfidf_vector, prediction, n=10):
        """
        Get top N features contributing to prediction
        
        Args:
            tfidf_vector: TF-IDF vector of the text
            prediction: Predicted class
            n: Number of top features
            
        Returns:
            list: Top contributing features
        """
        # Get feature importances from the model
        if prediction == 'spam':
            # Log probabilities for spam class
            feature_log_prob = self.model.feature_log_prob_[1]
        else:
            # Log probabilities for ham class
            feature_log_prob = self.model.feature_log_prob_[0]
        
        # Get non-zero features from the text
        non_zero_indices = tfidf_vector.nonzero()[1]
        
        if len(non_zero_indices) == 0:
            return []
        
        # Calculate contribution scores
        contributions = []
        for idx in non_zero_indices:
            word = self.feature_names[idx]
            tfidf_score = tfidf_vector[0, idx]
            log_prob = feature_log_prob[idx]
            
            # Contribution = TF-IDF score * log probability
            contribution = tfidf_score * np.exp(log_prob)
            
            contributions.append({
                'word': word,
                'contribution': float(contribution),
                'tfidf_score': float(tfidf_score)
            })
        
        # Sort by contribution
        contributions.sort(key=lambda x: x['contribution'], reverse=True)
        
        return contributions[:n]
    
    def _generate_explanation(self, prediction, confidence, top_features):
        """Generate human-readable explanation"""
        if prediction == 'spam':
            if confidence >= 90:
                base = "This email is HIGHLY LIKELY spam."
            elif confidence >= 70:
                base = "This email appears to be spam."
            else:
                base = "This email shows some spam characteristics."
            
            if top_features:
                keywords = ', '.join([f['word'] for f in top_features[:3]])
                return f"{base} Key indicators: {keywords}. These words are commonly found in spam messages."
            else:
                return f"{base} Overall text pattern matches spam emails."
        else:
            if confidence >= 90:
                base = "This email is HIGHLY LIKELY legitimate."
            elif confidence >= 70:
                base = "This email appears to be legitimate."
            else:
                base = "This email shows characteristics of legitimate mail."
            
            return f"{base} The content and language patterns match normal communication."
    
    def _explain_confidence(self, confidence):
        """Explain what the confidence score means"""
        if confidence >= 95:
            return "Very High Confidence - The model is almost certain about this classification."
        elif confidence >= 85:
            return "High Confidence - Strong indicators support this classification."
        elif confidence >= 70:
            return "Moderate Confidence - Clear patterns support this classification."
        elif confidence >= 60:
            return "Low-Moderate Confidence - Some patterns support this classification."
        else:
            return "Low Confidence - The classification is uncertain. Manual review recommended."
    
    def highlight_text(self, text, suspicious_words):
        """
        Highlight suspicious words in text
        
        Args:
            text (str): Original text
            suspicious_words (list): Words to highlight
            
        Returns:
            str: Text with HTML highlighting
        """
        highlighted = text
        
        for word in suspicious_words:
            # Case-insensitive replacement
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            highlighted = pattern.sub(
                f'<mark style="background-color: #FFE5E5; padding: 2px 4px; border-radius: 3px;">{word}</mark>',
                highlighted
            )
        
        return highlighted