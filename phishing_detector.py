"""
Phishing Detection Module
Analyzes URLs and email content for phishing indicators
"""

import re
from urllib.parse import urlparse
import tldextract


class PhishingDetector:
    """Detects phishing attempts in emails"""
    
    # Suspicious TLDs often used in phishing
    SUSPICIOUS_TLDS = {
        'tk', 'ml', 'ga', 'cf', 'gq', 'xyz', 'top', 'work', 'click',
        'link', 'download', 'racing', 'accountant', 'loan', 'win', 'bid'
    }
    
    # URL shorteners
    URL_SHORTENERS = {
        'bit.ly', 'goo.gl', 'tinyurl.com', 'ow.ly', 't.co', 'is.gd',
        'buff.ly', 'adf.ly', 'short.link', 'cutt.ly', 'rb.gy'
    }
    
    # Legitimate domains often impersonated
    IMPERSONATED_DOMAINS = {
        'paypal', 'amazon', 'microsoft', 'google', 'apple', 'facebook',
        'netflix', 'instagram', 'linkedin', 'twitter', 'dropbox', 'adobe',
        'ebay', 'wellsfargo', 'chase', 'bankofamerica', 'irs', 'usps', 'fedex', 'dhl'
    }
    
    def __init__(self):
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
    
    def analyze_email(self, email_text, email_html=None):
        """
        Analyze email for phishing indicators
        
        Args:
            email_text (str): Plain text email content
            email_html (str): HTML email content (optional)
            
        Returns:
            dict: Phishing analysis results
        """
        # Extract URLs
        urls = self._extract_urls(email_text)
        
        if not urls:
            return {
                'phishing_score': 0,
                'risk_level': 'Low',
                'url_count': 0,
                'suspicious_urls': [],
                'indicators': [],
                'explanation': 'No URLs found in email.'
            }
        
        # Analyze each URL
        suspicious_urls = []
        indicators = []
        total_risk_score = 0
        
        for url in urls:
            url_analysis = self._analyze_url(url)
            total_risk_score += url_analysis['risk_score']
            
            if url_analysis['is_suspicious']:
                suspicious_urls.append({
                    'url': url,
                    'reasons': url_analysis['reasons']
                })
                indicators.extend(url_analysis['reasons'])
        
        # Calculate overall phishing score (0-100)
        phishing_score = min(100, (total_risk_score / len(urls)) * 10)
        
        # Determine risk level
        if phishing_score >= 70:
            risk_level = 'High'
        elif phishing_score >= 40:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        # Generate explanation
        explanation = self._generate_explanation(phishing_score, indicators, len(urls))
        
        return {
            'phishing_score': round(phishing_score, 2),
            'risk_level': risk_level,
            'url_count': len(urls),
            'suspicious_urls': suspicious_urls,
            'indicators': list(set(indicators)),  # Remove duplicates
            'explanation': explanation
        }
    
    def _extract_urls(self, text):
        """Extract all URLs from text"""
        if not text:
            return []
        
        urls = self.url_pattern.findall(text)
        return list(set(urls))  # Remove duplicates
    
    def _analyze_url(self, url):
        """
        Analyze single URL for phishing indicators
        
        Returns:
            dict: URL analysis with risk score and reasons
        """
        reasons = []
        risk_score = 0
        
        try:
            parsed = urlparse(url)
            extracted = tldextract.extract(url)
            
            # Check 1: IP address instead of domain
            if self._is_ip_address(parsed.netloc):
                reasons.append('Uses IP address instead of domain name')
                risk_score += 8
            
            # Check 2: Suspicious TLD
            if extracted.suffix.lower() in self.SUSPICIOUS_TLDS:
                reasons.append(f'Suspicious domain extension (.{extracted.suffix})')
                risk_score += 6
            
            # Check 3: URL shortener
            if extracted.domain in self.URL_SHORTENERS:
                reasons.append('Uses URL shortener (hides real destination)')
                risk_score += 7
            
            # Check 4: Excessive subdomains
            subdomain_count = len(extracted.subdomain.split('.')) if extracted.subdomain else 0
            if subdomain_count > 2:
                reasons.append(f'Excessive subdomains ({subdomain_count})')
                risk_score += 5
            
            # Check 5: Domain impersonation
            for legit_domain in self.IMPERSONATED_DOMAINS:
                if legit_domain in extracted.domain and extracted.domain != legit_domain:
                    reasons.append(f'Possible impersonation of {legit_domain}')
                    risk_score += 9
            
            # Check 6: Suspicious characters in domain
            if re.search(r'[0-9]{4,}', extracted.domain):
                reasons.append('Domain contains many numbers')
                risk_score += 4
            
            # Check 7: Very long URL
            if len(url) > 150:
                reasons.append('Unusually long URL')
                risk_score += 3
            
            # Check 8: @ symbol in URL (username in URL)
            if '@' in parsed.netloc:
                reasons.append('Contains @ symbol (redirect trick)')
                risk_score += 8
            
            # Check 9: Double slashes in path
            if '//' in parsed.path:
                reasons.append('Double slashes in URL path')
                risk_score += 5
            
        except Exception as e:
            reasons.append('Malformed URL structure')
            risk_score += 6
        
        return {
            'is_suspicious': len(reasons) > 0,
            'risk_score': risk_score,
            'reasons': reasons
        }
    
    def _is_ip_address(self, hostname):
        """Check if hostname is an IP address"""
        ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        return bool(ip_pattern.match(hostname.split(':')[0]))
    
    def _generate_explanation(self, score, indicators, url_count):
        """Generate human-readable explanation"""
        if score >= 70:
            return f"HIGH RISK: Found {url_count} URL(s) with {len(indicators)} phishing indicators. This email shows strong signs of phishing."
        elif score >= 40:
            return f"MEDIUM RISK: Found {url_count} URL(s) with some suspicious patterns. Exercise caution before clicking links."
        else:
            if url_count > 0:
                return f"LOW RISK: Found {url_count} URL(s) with minimal suspicious indicators."
            else:
                return "No URLs detected in this email."