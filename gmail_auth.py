"""
Gmail OAuth2 Authentication Handler
Handles Google login and token management
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import config


class GmailAuthenticator:
    """Handles Gmail OAuth2 authentication"""
    
    def __init__(self):
        self.creds = None
        self.service = None
    
    def authenticate(self):
        """
        Authenticate user with Gmail OAuth2
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        # Check if credentials.json exists
        if not os.path.exists(config.CREDENTIALS_FILE):
            return False, "credentials.json not found. Please follow GMAIL_SETUP_GUIDE.md"
        
        # Load existing token if available
        if os.path.exists(config.TOKEN_FILE):
            try:
                self.creds = Credentials.from_authorized_user_file(
                    config.TOKEN_FILE, 
                    config.SCOPES
                )
            except Exception as e:
                print(f"Error loading token: {e}")
                self.creds = None
        
        # If no valid credentials, let user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    self.creds = None
            
            if not self.creds:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        config.CREDENTIALS_FILE, 
                        config.SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                except Exception as e:
                    return False, f"OAuth error: {str(e)}"
            
            # Save credentials for next run
            try:
                with open(config.TOKEN_FILE, 'w') as token:
                    token.write(self.creds.to_json())
            except Exception as e:
                print(f"Warning: Could not save token: {e}")
        
        # Build Gmail service
        try:
            self.service = build('gmail', 'v1', credentials=self.creds)
            return True, "Authentication successful"
        except Exception as e:
            return False, f"Failed to build Gmail service: {str(e)}"
    
    def get_service(self):
        """
        Get authenticated Gmail service
        
        Returns:
            Gmail service object or None
        """
        if not self.service:
            success, message = self.authenticate()
            if not success:
                return None
        return self.service
    
    def is_authenticated(self):
        """
        Check if user is authenticated
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.service is not None
    
    def logout(self):
        """Logout user by removing token file"""
        if os.path.exists(config.TOKEN_FILE):
            try:
                os.remove(config.TOKEN_FILE)
                self.creds = None
                self.service = None
                return True, "Logged out successfully"
            except Exception as e:
                return False, f"Logout error: {str(e)}"
        return True, "Already logged out"
    
    def get_user_email(self):
        """
        Get authenticated user's email address
        
        Returns:
            str: User email or None
        """
        if not self.service:
            return None
        
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile.get('emailAddress')
        except Exception as e:
            print(f"Error getting user email: {e}")
            return None