"""
Gmail Spam Classifier - PUBLIC DEPLOYMENT VERSION
Manual text input only (no Gmail OAuth)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Import predictor only
from predictor import SpamPredictor


# Page configuration
st.set_page_config(
    page_title="AI Spam Email Classifier ( Demo version)",
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
    }
    .stButton>button:hover {
        background-color: #FF6B6B;
    }
    .spam-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #FFE5E5;
        border-left: 5px solid #FF4B4B;
        margin: 1rem 0;
    }
    .ham-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #E5F5E5;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize predictor
@st.cache_resource
def load_predictor():
    """Load spam predictor (cached)"""
    return SpamPredictor()


def main():
    """Main application"""
    
    # Header
    st.title("🤖 AI Spam Email Classifier ( Demo version )")
    st.markdown("### Powered by Machine Learning - Naive Bayes Algorithm")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This AI-powered spam classifier uses a **Naive Bayes** 
        machine learning model trained on thousands of emails.
        
        **Model Stats:**
        - Algorithm: Multinomial Naive Bayes
        - Accuracy: ~97%
        - Features: TF-IDF (3000 features)
        - Training Set: SMS Spam Collection
        
        **How It Works:**
        1. Text preprocessing (stemming, stopwords)
        2. TF-IDF vectorization
        3. Probabilistic classification
        4. Confidence score calculation
        """)
        
        st.markdown("---")
        
        st.header("📊 Example Messages")
        
        if st.button("📩 Load Spam Example"):
            st.session_state.example_text = "URGENT! You have won a $5000 prize. Click here immediately to claim your reward before it expires. Limited time offer! Call 1-800-WINNER now!"
        
        if st.button("✉️ Load Legitimate Example"):
            st.session_state.example_text = "Hey Sarah, just confirming our meeting tomorrow at 3 PM at the coffee shop downtown. Let me know if you need to reschedule. Looking forward to catching up!"
        
        st.markdown("---")
        st.markdown("**Technologies:**")
        st.markdown("- Python 🐍")
        st.markdown("- Streamlit 🎈")
        st.markdown("- Scikit-learn 🤖")
        st.markdown("- NLTK 📝")
    
    # Load predictor
    try:
        predictor = load_predictor()
        
        if not predictor.is_loaded():
            st.error("⚠️ Model not loaded. Please ensure model files exist.")
            st.stop()
    except Exception as e:
        st.error(f"⚠️ Error loading model: {str(e)}")
        st.stop()
    
    # Main content
    st.subheader("📝 Enter Email Text")
    
    default_text = st.session_state.get('example_text', '')
    email_text = st.text_area(
        "Paste your email content here:",
        value=default_text,
        height=250,
        placeholder="Type or paste email message here...\n\nExample:\n'Congratulations! You have won a free iPhone. Click here to claim now!'",
        help="Enter the full email text including subject and body"
    )
    
    # Buttons
    col_clear, col_classify = st.columns([1, 2])
    
    with col_clear:
        if st.button("🗑️ Clear"):
            st.session_state.example_text = ''
            st.rerun()
    
    with col_classify:
        classify_button = st.button("🔍 Classify Email")
    
    # Process classification
    if classify_button:
        if not email_text.strip():
            st.warning("⚠️ Please enter some text to classify!")
        else:
            with st.spinner("🤖 Analyzing email..."):
                prediction, confidence = predictor.predict(email_text)
                
                st.markdown("---")
                st.subheader("📊 Classification Result")
                
                # Display result
                if prediction == 'spam':
                    st.markdown(f"""
                    <div class="spam-box">
                        <h2 style='color: #D32F2F; margin: 0;'>🚫 SPAM DETECTED</h2>
                        <p style='font-size: 1.2rem; margin-top: 0.5rem;'>
                            Confidence: <b>{confidence:.2f}%</b>
                        </p>
                        <p style='margin-top: 1rem;'>
                            ⚠️ This email appears to be spam. Be cautious and avoid clicking any links.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="ham-box">
                        <h2 style='color: #388E3C; margin: 0;'>✅ LEGITIMATE EMAIL</h2>
                        <p style='font-size: 1.2rem; margin-top: 0.5rem;'>
                            Confidence: <b>{confidence:.2f}%</b>
                        </p>
                        <p style='margin-top: 1rem;'>
                            ✓ This email appears to be legitimate (not spam).
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Confidence meter
                st.subheader("📈 Confidence Score")
                st.progress(confidence / 100)
                
                # Detailed analysis
                with st.expander("🔬 Technical Details"):
                    st.write(f"**Input Length:** {len(email_text)} characters")
                    st.write(f"**Word Count:** {len(email_text.split())} words")
                    st.write(f"**Classification:** {prediction.upper()}")
                    st.write(f"**Confidence:** {confidence:.4f}%")
                    
                    preprocessed = predictor.preprocess_text(email_text)
                    st.write(f"**Preprocessed Text (first 200 chars):**")
                    st.code(preprocessed[:200] + "..." if len(preprocessed) > 200 else preprocessed)
    
    # Features section
    st.markdown("---")
    st.subheader("✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🎯 High Accuracy**
        - 97%+ on test data
        - Trained on real spam
        - TF-IDF features
        """)
    
    with col2:
        st.markdown("""
        **⚡ Fast Processing**
        - Real-time prediction
        - <100ms response
        - Efficient algorithm
        """)
    
    with col3:
        st.markdown("""
        **🔒 Privacy First**
        - No data stored
        - Local processing
        - Fully anonymous
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 1rem;'>
            Made by Saiyam Jain
            <a href='https://github.com' target='_blank'>GitHub</a> | 
            <a href='https://streamlit.io' target='_blank'>Streamlit</a>
        </div>
                <div style='text-align: center; color: #666; padding: 1rem;'>
            contact me for full version with Gmail integration!
                email: deepakriyajain@gmail.com
           
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()