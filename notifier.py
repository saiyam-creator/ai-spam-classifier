"""
Real-time Email Monitoring & Notification System
Monitors Gmail for new spam and sends alerts
"""

import time
import threading
from datetime import datetime, timedelta
from plyer import notification
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailNotifier:
    """Monitors Gmail and sends notifications for spam/phishing"""
    
    def __init__(self, gmail_service, predictor, phishing_detector, check_interval=300):
        """
        Initialize notifier
        
        Args:
            gmail_service: Authenticated Gmail API service
            predictor: SpamPredictor instance
            phishing_detector: PhishingDetector instance
            check_interval: Seconds between checks (default 5 minutes)
        """
        self.gmail_service = gmail_service
        self.predictor = predictor
        self.phishing_detector = phishing_detector
        self.check_interval = check_interval
        
        self.is_running = False
        self.monitor_thread = None
        self.last_check_time = datetime.now()
        
        self.alert_queue = []
        self.notification_enabled = True
    
    def start_monitoring(self):
        """Start background monitoring"""
        if self.is_running:
            return False, "Monitoring already running"
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        return True, "Monitoring started"
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        return True, "Monitoring stopped"
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                self._check_new_emails()
            except Exception as e:
                print(f"Monitoring error: {e}")
            
            # Wait for next check
            time.sleep(self.check_interval)
    
    def _check_new_emails(self):
        """Check for new emails since last check"""
        try:
            from gmail_fetch import GmailFetcher
            
            # Calculate time since last check
            time_ago = datetime.now() - self.last_check_time
            query = f'after:{int(time_ago.total_seconds())}s'
            
            # Fetch recent emails
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return
            
            # Analyze each new email
            fetcher = GmailFetcher(self.gmail_service)
            
            for msg in messages:
                email_data = fetcher._get_email_details(msg['id'])
                
                if email_data:
                    self._analyze_and_notify(email_data)
            
            # Update last check time
            self.last_check_time = datetime.now()
            
        except Exception as e:
            print(f"Error checking emails: {e}")
    
    def _analyze_and_notify(self, email_data):
        """Analyze email and send notification if needed"""
        from gmail_fetch import GmailFetcher
        
        # Get email text
        fetcher = GmailFetcher(self.gmail_service)
        email_text = fetcher.get_email_text_for_classification(email_data)
        
        # Spam prediction
        prediction, confidence = self.predictor.predict(email_text)
        
        # Phishing detection
        phishing_result = self.phishing_detector.analyze_email(email_text)
        
        # Check if notification needed
        should_notify = False
        alert_type = None
        
        if prediction == 'spam' and confidence >= 80:
            should_notify = True
            alert_type = 'spam'
        
        if phishing_result['phishing_score'] >= 70:
            should_notify = True
            alert_type = 'phishing'
        
        if should_notify:
            alert = {
                'timestamp': datetime.now(),
                'subject': email_data['subject'],
                'sender': email_data['sender'],
                'type': alert_type,
                'spam_confidence': confidence,
                'phishing_score': phishing_result['phishing_score']
            }
            
            self.alert_queue.append(alert)
            self._send_notification(alert)
    
    def _send_notification(self, alert):
        """Send desktop notification"""
        if not self.notification_enabled:
            return
        
        try:
            if alert['type'] == 'spam':
                title = "🚫 Spam Email Detected"
                message = f"From: {alert['sender'][:30]}\nSubject: {alert['subject'][:40]}\nConfidence: {alert['spam_confidence']:.0f}%"
            else:
                title = "⚠️ Phishing Attempt Detected"
                message = f"From: {alert['sender'][:30]}\nSubject: {alert['subject'][:40]}\nRisk: {alert['phishing_score']:.0f}%"
            
            notification.notify(
                title=title,
                message=message,
                app_name='Gmail Spam Classifier',
                timeout=10
            )
        except Exception as e:
            print(f"Notification error: {e}")
    
    def get_recent_alerts(self, limit=10):
        """Get recent alerts"""
        return self.alert_queue[-limit:] if len(self.alert_queue) > 0 else []
    
    def clear_alerts(self):
        """Clear alert queue"""
        self.alert_queue = []
    
    def get_status(self):
        """Get monitoring status"""
        return {
            'is_running': self.is_running,
            'last_check': self.last_check_time.strftime('%Y-%m-%d %H:%M:%S'),
            'alert_count': len(self.alert_queue),
            'check_interval': self.check_interval
        }