"""
Configuration settings for Gmail Spam Classifier
"""

import os

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_DIR = os.path.join(BASE_DIR, 'credentials')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# OAuth credentials
CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(CREDENTIALS_DIR, 'token.json')

# Model files
MODEL_FILE = os.path.join(MODELS_DIR, 'model.pkl')
VECTORIZER_FILE = os.path.join(MODELS_DIR, 'vectorizer.pkl')

# Gmail API settings
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# EMAIL FETCHING SETTINGS - UPDATED
MAX_EMAILS = 500  # Maximum emails to fetch (increased from 20)
BATCH_SIZE = 100  # Number of emails per API request (Gmail max is 500, but 100 is safer)

# FOLDER/LABEL SETTINGS - NEW
# Fetch from all folders to include spam emails that Gmail already filtered
SEARCH_QUERY = 'in:anywhere'  # Fetches from ALL folders including SPAM

# Labels to track for analysis
TRACK_LABELS = [
    'INBOX',
    'SPAM',
    'IMPORTANT',
    'PROMOTIONS',
    'SOCIAL',
    'CATEGORY_PERSONAL',
    'CATEGORY_SOCIAL',
    'CATEGORY_PROMOTIONS',
    'CATEGORY_UPDATES',
    'CATEGORY_FORUMS'
]

# Create credentials directory if it doesn't exist
os.makedirs(CREDENTIALS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)