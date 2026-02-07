"""
Gmail Spam Classifier - PUBLIC DEPLOYMENT VERSION
Advanced spam detection with phishing analysis and AI explanations
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re

# Import modules
from predictor import SpamPredictor
from phishing_detector import PhishingDetector
from explainability import SpamExplainer


# Page configuration
st.set_page_config(
    page_title="AI Spam Email Classifier - Demo",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 10px;
        border: none;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FF6B6B;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
    }
    .spam-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #FFE5E5;
        border-left: 5px solid #FF4B4B;
        margin: 1rem 0;
        animation: slideIn 0.3s ease;
    }
    .ham-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #E5F5E5;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
        animation: slideIn 0.3s ease;
    }
    .phishing-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        border: 2px solid #ddd;
    }
    .feature-card {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 8px;
        background-color: #f8f9fa;
        border-left: 4px solid #FF4B4B;
    }
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .highlight-word {
        background-color: #FFE5E5;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
        color: #D32F2F;
    }
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
@st.cache_resource
def load_predictor():
    """Load spam predictor (cached)"""
    return SpamPredictor()


def init_session_state():
    """Initialize all session state variables"""
    if 'predictor' not in st.session_state:
        st.session_state.predictor = load_predictor()
    
    if 'phishing_detector' not in st.session_state:
        st.session_state.phishing_detector = PhishingDetector()
    
    if 'explainer' not in st.session_state:
        if st.session_state.predictor.is_loaded():
            model, vectorizer = st.session_state.predictor.get_model_and_vectorizer()
            st.session_state.explainer = SpamExplainer(model, vectorizer)
        else:
            st.session_state.explainer = None
    
    if 'example_text' not in st.session_state:
        st.session_state.example_text = ''
    
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []


def render_sidebar():
    """Render sidebar content"""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/spam.png", width=80)
        st.title("About")
        
        st.markdown("""
        ### 🤖 AI Spam Classifier
        
        Advanced email security powered by machine learning and phishing detection.
        
        **🎯 Model Performance:**
        - Algorithm: Multinomial Naive Bayes
        - Accuracy: ~97%
        - Features: 3000 TF-IDF vectors
        - Dataset: SMS Spam Collection
        
        **🔍 Detection Methods:**
        1. **Text Analysis** - ML pattern recognition
        2. **Phishing Detection** - URL security scan
        3. **AI Explainability** - Why it's spam
        
        **⚡ Processing Pipeline:**
        - Text preprocessing (lowercase, stemming)
        - Stopword removal
        - TF-IDF vectorization
        - Probabilistic classification
        - Multi-factor risk scoring
        """)
        
        st.markdown("---")
        
        st.header("📊 Quick Examples")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚫 Spam", use_container_width=True):
                st.session_state.example_text = """URGENT WINNER NOTIFICATION!
                
Congratulations! You've been selected to receive a $5,000 cash prize and a FREE iPhone 15 Pro Max!

To claim your reward, click here immediately: http://bit.ly/claim-prize-now

This offer expires in 24 hours! Act now before it's too late!

Call our hotline: 1-800-FAKE-NUM
Reference Code: WIN5000XYZ

Don't miss this once-in-a-lifetime opportunity!"""
                st.rerun()
        
        with col2:
            if st.button("✅ Legit", use_container_width=True):
                st.session_state.example_text = """Hi Sarah,

Just wanted to confirm our meeting tomorrow at 3 PM at the downtown Starbucks. I'll bring the project documents we discussed.

Let me know if you need to reschedule or if there's anything specific you'd like me to prepare.

Looking forward to catching up!

Best regards,
Mike"""
                st.rerun()
        
        st.markdown("---")
        
        # Statistics
        if len(st.session_state.analysis_history) > 0:
            st.header("📈 Your Stats")
            total = len(st.session_state.analysis_history)
            spam_count = sum(1 for x in st.session_state.analysis_history if x['prediction'] == 'spam')
            
            st.metric("Total Analyzed", total)
            st.metric("Spam Detected", spam_count)
            st.metric("Spam Rate", f"{(spam_count/total*100):.1f}%")
        
        st.markdown("---")
        st.markdown("**🛠️ Technologies:**")
        st.markdown("- Python 🐍")
        st.markdown("- Streamlit 🎈")
        st.markdown("- Scikit-learn 🤖")
        st.markdown("- NLTK 📝")
        st.markdown("- TF-IDF Vectorization")


def display_classification_result(email_text, prediction, confidence, phishing_result, explanation):
    """Display comprehensive classification results"""
    
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Main results in two columns
    col_spam, col_phishing = st.columns(2)
    
    with col_spam:
        if prediction == 'spam':
            st.markdown(f"""
            <div class="spam-box">
                <h2 style='margin: 0; color: #D32F2F;'>🚫 SPAM DETECTED</h2>
                <p style='font-size: 1.3rem; margin-top: 0.5rem; font-weight: bold;'>
                    Confidence: {confidence:.2f}%
                </p>
                <p style='margin-top: 1rem; color: #555;'>
                    ⚠️ This email appears to be spam. Exercise caution and avoid clicking any links.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ham-box">
                <h2 style='margin: 0; color: #388E3C;'>✅ LEGITIMATE EMAIL</h2>
                <p style='font-size: 1.3rem; margin-top: 0.5rem; font-weight: bold;'>
                    Confidence: {confidence:.2f}%
                </p>
                <p style='margin-top: 1rem; color: #555;'>
                    ✓ This email appears to be legitimate communication.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Confidence meter
        st.markdown("#### 📈 Confidence Level")
        st.progress(confidence / 100)
        
        if confidence >= 90:
            st.success("Very High Confidence")
        elif confidence >= 70:
            st.info("High Confidence")
        elif confidence >= 50:
            st.warning("Moderate Confidence")
        else:
            st.error("Low Confidence - Manual Review Recommended")
    
    with col_phishing:
        risk_color = {'Low': '#4CAF50', 'Medium': '#FF9800', 'High': '#D32F2F'}
        risk_bg = {'Low': '#E8F5E9', 'Medium': '#FFF3E0', 'High': '#FFEBEE'}
        
        st.markdown(f"""
        <div style='padding: 1.5rem; border-radius: 10px; background-color: {risk_bg[phishing_result["risk_level"]]}; border: 2px solid {risk_color[phishing_result["risk_level"]]}'>
            <h2 style='margin: 0;'>🔗 Phishing Risk Analysis</h2>
            <p style='font-size: 1.3rem; margin-top: 0.5rem; font-weight: bold;'>
                Risk Score: {phishing_result['phishing_score']:.1f}/100
            </p>
            <p style='color: {risk_color[phishing_result['risk_level']]}; font-size: 1.2rem; font-weight: bold; margin-top: 0.5rem;'>
                ⚠️ {phishing_result['risk_level']} Risk Level
            </p>
            <p style='margin-top: 1rem; color: #555;'>
                {phishing_result['explanation']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**URLs Found:** {phishing_result['url_count']}")
        if phishing_result['suspicious_urls']:
            st.markdown(f"**Suspicious URLs:** {len(phishing_result['suspicious_urls'])}")
    
    # AI Explanation Section
    if explanation:
        st.markdown("---")
        st.markdown("## 🧠 AI Explanation: Why This Classification?")
        
        st.info(f"**{explanation['explanation']}**")
        
        # Show suspicious words with highlighting
        if explanation['suspicious_words']:
            st.markdown("### 🔍 Key Spam Indicators")
            
            # Display highlighted words
            highlighted_words = ' '.join([
                f'<span class="highlight-word">{word}</span>' 
                for word in explanation['suspicious_words']
            ])
            st.markdown(f"**Detected Keywords:** {highlighted_words}", unsafe_allow_html=True)
        
        # Detailed feature analysis
        with st.expander("📊 Detailed Feature Analysis", expanded=False):
            st.markdown("**Top Contributing Features:**")
            
            if explanation['top_features']:
                # Create DataFrame for better visualization
                features_df = pd.DataFrame(explanation['top_features'][:10])
                features_df['contribution'] = features_df['contribution'].round(6)
                features_df['tfidf_score'] = features_df['tfidf_score'].round(6)
                
                st.dataframe(
                    features_df,
                    column_config={
                        "word": "Word/Feature",
                        "contribution": st.column_config.NumberColumn(
                            "Contribution Score",
                            format="%.6f"
                        ),
                        "tfidf_score": st.column_config.NumberColumn(
                            "TF-IDF Score",
                            format="%.6f"
                        ),
                    },
                    hide_index=True,
                    use_container_width=True
                )
            
            st.markdown(f"**Confidence Reasoning:** {explanation['confidence_reasoning']}")
    
    # Phishing Details
    if phishing_result['phishing_score'] > 0:
        with st.expander("⚠️ Phishing Analysis Details", expanded=phishing_result['risk_level'] == 'High'):
            
            if phishing_result['indicators']:
                st.markdown("**🚨 Security Risk Indicators:**")
                for i, indicator in enumerate(phishing_result['indicators'], 1):
                    st.markdown(f"{i}. {indicator}")
            
            if phishing_result['suspicious_urls']:
                st.markdown("---")
                st.markdown("**🔗 Suspicious URLs Detected:**")
                
                for idx, url_data in enumerate(phishing_result['suspicious_urls'], 1):
                    st.markdown(f"**URL #{idx}:**")
                    st.code(url_data['url'], language=None)
                    
                    st.markdown("**Why it's suspicious:**")
                    for reason in url_data['reasons']:
                        st.markdown(f"- ⚠️ {reason}")
                    
                    st.markdown("---")
    
    # Technical Details
    with st.expander("🔬 Technical Analysis", expanded=False):
        col_tech1, col_tech2 = st.columns(2)
        
        with col_tech1:
            st.markdown("**Text Statistics:**")
            st.write(f"- Characters: {len(email_text)}")
            st.write(f"- Words: {len(email_text.split())}")
            st.write(f"- Lines: {len(email_text.splitlines())}")
            
            # Count URLs
            url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
            urls = url_pattern.findall(email_text)
            st.write(f"- URLs: {len(urls)}")
        
        with col_tech2:
            st.markdown("**Classification Details:**")
            st.write(f"- Prediction: **{prediction.upper()}**")
            st.write(f"- ML Confidence: **{confidence:.4f}%**")
            st.write(f"- Phishing Score: **{phishing_result['phishing_score']:.2f}/100**")
            st.write(f"- Risk Level: **{phishing_result['risk_level']}**")
        
        st.markdown("**Preprocessed Text Preview:**")
        preprocessed = st.session_state.predictor.preprocess_text(email_text)
        preview_length = min(300, len(preprocessed))
        st.code(preprocessed[:preview_length] + ("..." if len(preprocessed) > preview_length else ""), language=None)


def main():
    """Main application"""
    
    # Initialize session state
    init_session_state()
    
    # Check if predictor loaded
    if not st.session_state.predictor.is_loaded():
        st.error("⚠️ Model failed to load. Please refresh the page or contact support.")
        st.stop()
    
    # Render sidebar
    render_sidebar()
    
    # Main header
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='font-size: 3rem; margin: 0;'>🤖 AI Spam Email Classifier ( Demo Version )</h1>
        <p style='font-size: 1.3rem; color: #666; margin-top: 0.5rem;'>
            Advanced ML-Powered Email Security Analysis
        </p>
        <p style='color: rgb(255, 75, 75); font-size: 0.9rem;'>
            🎯 97% Accuracy | 🔍 Phishing Detection | 🧠 AI Explanations | ⚡ Real-time Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main input section
    st.markdown("## 📝 Enter Email Content")
    
    email_text = st.text_area(
        "Paste your email content here:",
        value=st.session_state.example_text,
        height=300,
        placeholder="""Type or paste the complete email here...

Example:
Subject: Urgent Account Verification Required
From: security@paypa1-verify.com

Dear Customer,

Your account has been temporarily suspended due to unusual activity...
        
Include both subject and body for best results.""",
        help="Enter the full email text including subject and body for comprehensive analysis"
    )
    
    # Action buttons
    col_clear, col_classify = st.columns([1, 3])
    
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.example_text = ''
            st.rerun()
    
    with col_classify:
        classify_button = st.button("🔍 Analyze Email", use_container_width=True, type="primary")
    
    # Process classification
    if classify_button:
        if not email_text.strip():
            st.warning("⚠️ Please enter some text to analyze!")
        else:
            with st.spinner("🤖 Running comprehensive analysis..."):
                # Spam prediction
                prediction, confidence = st.session_state.predictor.predict(email_text)
                
                # Phishing detection
                phishing_result = st.session_state.phishing_detector.analyze_email(email_text)
                
                # Get explanation
                explanation = None
                if st.session_state.explainer:
                    explanation = st.session_state.explainer.explain_prediction(
                        email_text, prediction, confidence
                    )
                
                # Store in history
                st.session_state.analysis_history.append({
                    'timestamp': datetime.now(),
                    'prediction': prediction,
                    'confidence': confidence,
                    'phishing_score': phishing_result['phishing_score']
                })
                
                # Display results
                display_classification_result(
                    email_text, 
                    prediction, 
                    confidence, 
                    phishing_result, 
                    explanation
                )
    
    # Features showcase
    st.markdown("---")
    st.markdown("## ✨ Platform Features")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style='margin: 0; color: #FF4B4B;'>🎯</h3>
            <h4 style='color: #FF4B4B;'>97% Accuracy</h4>
            <p style='font-size: 0.9rem; color: #666;'>Trained on thousands of real spam emails</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style='margin: 0; color: #FF4B4B;'>⚡</h3>
            <h4 style='color: #FF4B4B;'>Real-time</h4>
            <p style='font-size: 0.9rem; color: #666;'>Instant analysis in <100ms</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style='margin: 0; color: #FF4B4B;'>🔍</h3>
            <h4 style='color: #FF4B4B;'>Phishing Detection</h4>
            <p style='font-size: 0.9rem; color: #666;'>Advanced URL & link analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style='margin: 0; color: #FF4B4B;'>🔒</h3>
            <h4 style='color: #FF4B4B;'>100% Private</h4>
            <p style='font-size: 0.9rem; color: #666;'>No data stored or shared</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0; background-color: #f8f9fa; border-radius: 10px;'>
            <p style='color: #FF4B4B; font-size: 1.1rem; font-weight: bold; margin: 0;'>
                Created by Saiyam Jain 💻
            </p>
            <p style='color: #666; margin-top: 0.5rem;'>
                ML Engineer | AI Developer | Cybersecurity Enthusiast
            </p>
            <p style='margin-top: 1rem;'>
                <a href='https://github.com' target='_blank' style='margin: 0 0.5rem; text-decoration: none;'>
                    🔗 GitHub
                </a>
                |
                <a href='mailto:deepakriyajain@gmail.com' style='margin: 0 0.5rem; text-decoration: none;'>
                    📧 Email
                </a>
                |
                <a href='https://streamlit.io' target='_blank' style='margin: 0 0.5rem; text-decoration: none;'>
                    🎈 Powered by Streamlit
                </a>
            </p>
            <div style='margin-top: 2rem; padding: 1rem; background-color: #fff; border-radius: 8px; border: 2px solid #FF4B4B;'>
                <p style='color: #FF4B4B; font-weight: bold; margin: 0;'>
                    💼 Want the Full Version with Gmail Integration?
                </p>
                <p style='color: #666; margin-top: 0.5rem;'>
                    Contact me for the professional version with real-time Gmail scanning,
                    automatic monitoring, and desktop notifications!
                </p>
                <p style='margin-top: 0.5rem;'>
                    📧 <a href='mailto:deepakriyajain@gmail.com'>deepakriyajain@gmail.com</a>
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()