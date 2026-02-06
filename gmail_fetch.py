"""
Gmail Email Fetcher - PRODUCTION VERSION
Fetches and parses emails from Gmail API with full pagination and all folders
"""

import base64
import re
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import config


class GmailFetcher:
    """Fetches emails from Gmail using authenticated service with pagination"""
    
    def __init__(self, service):
        """
        Initialize fetcher with Gmail service
        
        Args:
            service: Authenticated Gmail API service object
        """
        self.service = service
    
    def fetch_recent_emails(self, max_results=None, progress_callback=None):
        """
        Fetch recent emails from ALL folders (including SPAM) with pagination
        
        Args:
            max_results (int): Maximum number of emails to fetch
            progress_callback (callable): Optional callback function for progress updates
                                         Called with (current_count, total_fetched, status_message)
        
        Returns:
            list: List of email dictionaries
        """
        if max_results is None:
            max_results = config.MAX_EMAILS
        
        try:
            all_emails = []
            page_token = None
            total_fetched = 0
            
            # Fetch emails in batches with pagination
            while total_fetched < max_results:
                # Calculate how many to fetch in this batch
                batch_size = min(config.BATCH_SIZE, max_results - total_fetched)
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(total_fetched, max_results, f"Fetching batch... ({total_fetched}/{max_results})")
                
                # Fetch message list with pagination
                request_params = {
                    'userId': 'me',
                    'maxResults': batch_size,
                    'q': config.SEARCH_QUERY  # 'in:anywhere' - fetches from ALL folders
                }
                
                # Add page token for pagination (if not first request)
                if page_token:
                    request_params['pageToken'] = page_token
                
                results = self.service.users().messages().list(**request_params).execute()
                
                messages = results.get('messages', [])
                
                if not messages:
                    # No more messages
                    break
                
                # Fetch full message details for this batch
                for idx, msg in enumerate(messages):
                    email_data = self._get_email_details(msg['id'])
                    
                    if email_data:
                        all_emails.append(email_data)
                        total_fetched += 1
                        
                        # Update progress every 10 emails
                        if progress_callback and (total_fetched % 10 == 0 or total_fetched == max_results):
                            progress_callback(
                                total_fetched, 
                                max_results, 
                                f"Processing email {total_fetched}/{max_results}..."
                            )
                
                # Check if there's a next page
                page_token = results.get('nextPageToken')
                
                if not page_token:
                    # No more pages
                    break
            
            # Final progress update
            if progress_callback:
                progress_callback(total_fetched, max_results, f"Completed! Fetched {total_fetched} emails")
            
            return all_emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            if progress_callback:
                progress_callback(0, 0, f"Error: {str(e)}")
            return []
    
    def _get_email_details(self, msg_id):
        """
        Get detailed information for a specific email
        
        Args:
            msg_id (str): Gmail message ID
            
        Returns:
            dict: Email details including folder labels
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            subject = self._get_header(headers, 'Subject')
            sender = self._get_header(headers, 'From')
            date = self._get_header(headers, 'Date')
            
            # Extract body
            body = self._get_email_body(message['payload'])
            
            # Clean body text
            body_text = self._clean_body(body)
            
            # Extract labels/folders - CRITICAL FOR SPAM DETECTION
            labels = message.get('labelIds', [])
            folder_info = self._parse_labels(labels)
            
            return {
                'id': msg_id,
                'subject': subject or '(No Subject)',
                'sender': sender or '(Unknown)',
                'date': date or '(Unknown Date)',
                'body': body_text,
                'snippet': message.get('snippet', ''),
                'labels': labels,  # Raw Gmail labels
                'folder': folder_info['primary_folder'],  # Main folder (INBOX, SPAM, etc.)
                'is_spam_folder': folder_info['is_spam'],  # True if in SPAM folder
                'categories': folder_info['categories']  # PROMOTIONS, SOCIAL, etc.
            }
            
        except Exception as e:
            print(f"Error getting email {msg_id}: {e}")
            return None
    
    def _parse_labels(self, labels):
        """
        Parse Gmail labels to determine folder and categories
        
        Args:
            labels (list): List of Gmail label IDs
            
        Returns:
            dict: Parsed folder information
        """
        folder_info = {
            'primary_folder': 'INBOX',  # Default
            'is_spam': False,
            'categories': []
        }
        
        if not labels:
            return folder_info
        
        # Check for SPAM folder - MOST IMPORTANT
        if 'SPAM' in labels:
            folder_info['primary_folder'] = 'SPAM'
            folder_info['is_spam'] = True
        elif 'INBOX' in labels:
            folder_info['primary_folder'] = 'INBOX'
        elif 'IMPORTANT' in labels:
            folder_info['primary_folder'] = 'IMPORTANT'
        elif 'SENT' in labels:
            folder_info['primary_folder'] = 'SENT'
        elif 'DRAFT' in labels:
            folder_info['primary_folder'] = 'DRAFT'
        
        # Check for categories
        for label in labels:
            if label.startswith('CATEGORY_'):
                category = label.replace('CATEGORY_', '')
                folder_info['categories'].append(category)
                
                # If no primary folder set, use category
                if folder_info['primary_folder'] == 'INBOX' and not 'INBOX' in labels:
                    folder_info['primary_folder'] = category
        
        # Legacy category labels
        if 'PROMOTIONS' in labels:
            folder_info['categories'].append('PROMOTIONS')
        if 'SOCIAL' in labels:
            folder_info['categories'].append('SOCIAL')
        if 'FORUMS' in labels:
            folder_info['categories'].append('FORUMS')
        if 'UPDATES' in labels:
            folder_info['categories'].append('UPDATES')
        
        return folder_info
    
    def _get_header(self, headers, name):
        """
        Extract header value by name
        
        Args:
            headers (list): List of email headers
            name (str): Header name to find
            
        Returns:
            str: Header value or None
        """
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return None
    
    def _get_email_body(self, payload):
        """
        Extract email body from payload
        
        Args:
            payload (dict): Email payload
            
        Returns:
            str: Email body text
        """
        body = ""
        
        if 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8', errors='ignore')
        
        elif 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='ignore')
                        break
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        html = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='ignore')
                        body = self._html_to_text(html)
                        break
                elif 'parts' in part:
                    # Recursive for nested parts
                    body = self._get_email_body(part)
                    if body:
                        break
        
        return body
    
    def _html_to_text(self, html):
        """
        Convert HTML to plain text
        
        Args:
            html (str): HTML content
            
        Returns:
            str: Plain text
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()
        except Exception:
            return html
    
    def _clean_body(self, body):
        """
        Clean email body text
        
        Args:
            body (str): Raw body text
            
        Returns:
            str: Cleaned text
        """
        if not body:
            return ""
        
        # Remove extra whitespace
        body = re.sub(r'\s+', ' ', body)
        
        # Remove URLs (optional, but helps with spam detection)
        body = re.sub(r'http\S+|www.\S+', '', body)
        
        # Trim
        body = body.strip()
        
        return body
    
    def get_email_text_for_classification(self, email_data):
        """
        Get combined text for spam classification
        
        Args:
            email_data (dict): Email data dictionary
            
        Returns:
            str: Combined text (subject + body)
        """
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        
        # Combine subject and body for classification
        combined = f"{subject} {body}"
        
        return combined.strip()
    
    def get_statistics(self, emails):
        """
        Get statistics about fetched emails by folder
        
        Args:
            emails (list): List of email dictionaries
            
        Returns:
            dict: Statistics by folder
        """
        stats = {
            'total': len(emails),
            'by_folder': {},
            'spam_folder_count': 0,
            'inbox_count': 0
        }
        
        for email in emails:
            folder = email.get('folder', 'UNKNOWN')
            
            if folder not in stats['by_folder']:
                stats['by_folder'][folder] = 0
            
            stats['by_folder'][folder] += 1
            
            if email.get('is_spam_folder', False):
                stats['spam_folder_count'] += 1
            
            if folder == 'INBOX':
                stats['inbox_count'] += 1
        
        return stats