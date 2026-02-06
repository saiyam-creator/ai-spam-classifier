# 🔐 Gmail API Setup Guide - Complete Instructions

Follow these steps to enable Gmail API access for your spam classifier.

---

## 📋 Prerequisites

- Google Account (Gmail)
- Python 3.8+ installed
- Project files downloaded

---

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create New Project**
   - Click "Select a project" dropdown (top bar)
   - Click "NEW PROJECT"
   - Project name: `Gmail Spam Classifier`
   - Click "CREATE"
   - Wait for project creation (10-20 seconds)

3. **Select Your Project**
   - Make sure your new project is selected in the dropdown

---

### Step 2: Enable Gmail API

1. **Navigate to APIs & Services**
   - In the left sidebar, click "APIs & Services" → "Library"
   - Or visit: https://console.cloud.google.com/apis/library

2. **Search for Gmail API**
   - In the search bar, type: "Gmail API"
   - Click on "Gmail API" from results

3. **Enable the API**
   - Click the blue "ENABLE" button
   - Wait for activation (5-10 seconds)

---

### Step 3: Configure OAuth Consent Screen

1. **Go to OAuth Consent Screen**
   - Left sidebar: "APIs & Services" → "OAuth consent screen"
   - Or visit: https://console.cloud.google.com/apis/credentials/consent

2. **Choose User Type**
   - Select "External"
   - Click "CREATE"

3. **Fill in App Information**
   
   **App Information:**
   - App name: `Gmail Spam Classifier`
   - User support email: (your email)
   - Developer contact: (your email)

   **App Domain (Optional - can skip):**
   - Leave blank for testing

   Click "SAVE AND CONTINUE"

4. **Scopes**
   - Click "ADD OR REMOVE SCOPES"
   - Search: `.../auth/gmail.readonly`
   - Check the box for: `https://www.googleapis.com/auth/gmail.readonly`
   - Click "UPDATE"
   - Click "SAVE AND CONTINUE"

5. **Test Users**
   - Click "ADD USERS"
   - Enter your Gmail address (the one you'll test with)
   - Click "ADD"
   - Click "SAVE AND CONTINUE"

6. **Summary**
   - Review information
   - Click "BACK TO DASHBOARD"

---

### Step 4: Create OAuth Credentials

1. **Go to Credentials**
   - Left sidebar: "APIs & Services" → "Credentials"
   - Or visit: https://console.cloud.google.com/apis/credentials

2. **Create OAuth Client ID**
   - Click "+ CREATE CREDENTIALS" (top)
   - Select "OAuth client ID"

3. **Configure OAuth Client**
   - Application type: **Desktop app**
   - Name: `Gmail Spam Classifier Desktop`
   - Click "CREATE"

4. **Download Credentials**
   - A popup appears with your credentials
   - Click "DOWNLOAD JSON"
   - Save the file (it will be named something like `client_secret_XXX.json`)

---

### Step 5: Install Credentials in Project

1. **Rename the Downloaded File**
   - Rename `client_secret_XXX.json` to: `credentials.json`

2. **Create Credentials Folder**
```bash
   cd spam-classifier
   mkdir -p credentials
```

3. **Move Credentials File**
   - Move `credentials.json` into the `credentials/` folder
   - Final path: `spam-classifier/credentials/credentials.json`

4. **Verify File Location**
```bash
   # The file should be here:
   spam-classifier/
   └── credentials/
       └── credentials.json
```

---

### Step 6: Install Python Dependencies
```bash
# Make sure you're in the project directory
cd spam-classifier

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

This installs:
- ✅ Streamlit (web UI)
- ✅ Google API libraries (Gmail access)
- ✅ Scikit-learn (ML model)
- ✅ NLTK (text processing)
- ✅ BeautifulSoup (HTML parsing)

---

### Step 7: Train the Model (If Not Done)

If you haven't trained the spam classifier model yet:
```bash
python train_model.py
```

This creates:
- `models/model.pkl` (trained Naive Bayes classifier)
- `models/vectorizer.pkl` (TF-IDF vectorizer)
- `models/confusion_matrix.png` (performance chart)

**Expected output:**
```
Training Accuracy: 98.50%
Testing Accuracy: 97.31%
Model saved successfully!
```

---

### Step 8: Run the Application
```bash
streamlit run app.py
```

The app will:
1. Open in your browser automatically (http://localhost:8501)
2. Show the Gmail Spam Classifier dashboard
3. Display a "Login with Google" button

---

### Step 9: First-Time Login

1. **Click "Login with Google"**
   - A browser window opens automatically

2. **Choose Your Google Account**
   - Select the account you added as a test user

3. **Review Permissions**
   - Google shows: "Gmail Spam Classifier wants to access your Google Account"
   - Permissions requested: "Read your email messages and settings"

4. **Accept Warning (First Time Only)**
   - Google shows: "This app isn't verified"
   - Click "Advanced"
   - Click "Go to Gmail Spam Classifier (unsafe)"
   - This is normal for testing - it's YOUR app!

5. **Grant Permissions**
   - Click "Allow"
   - The browser closes automatically

6. **Return to App**
   - The app now shows "✅ Logged in as: your.email@gmail.com"
   - Token saved to: `credentials/token.json`

---

### Step 10: Scan Your Emails

1. **Click "Scan My Emails"**
   - The app fetches your 20 most recent inbox emails

2. **View Results**
   - Total emails scanned
   - Spam vs. legitimate count
   - Detailed table with predictions

3. **Export Results**
   - Download CSV report of all scanned emails

---

## 🔒 Security Notes

### Files to NEVER Commit to Git

Already protected by `.gitignore`:
- ✅ `credentials/credentials.json` (OAuth client secret)
- ✅ `credentials/token.json` (User access token)

### Token Storage

- `token.json` is created after first login
- Contains encrypted access token
- Valid for extended period
- Auto-refreshes when needed
- Delete to logout completely

### Permissions

The app ONLY requests:
- ✅ **Read-only** access to Gmail
- ❌ Cannot send emails
- ❌ Cannot delete emails
- ❌ Cannot modify emails

---

## 🐛 Troubleshooting

### Issue 1: "credentials.json not found"

**Cause:** OAuth credentials not in correct location

**Solution:**
```bash
# Check file exists:
ls credentials/credentials.json

# If not, download from Google Cloud Console:
# APIs & Services → Credentials → Download OAuth client
```

---

### Issue 2: "This app isn't verified"

**Cause:** Normal for apps in testing mode

**Solution:**
- Click "Advanced"
- Click "Go to Gmail Spam Classifier (unsafe)"
- This is YOUR app - it's safe!

**To Remove Warning (Optional):**
- Complete OAuth verification process (takes 1-2 weeks)
- Only needed for public apps

---

### Issue 3: "Access blocked: authorization error"

**Cause:** Email not added as test user

**Solution:**
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Click "Test users" section
3. Click "ADD USERS"
4. Add your Gmail address
5. Try logging in again

---

### Issue 4: "Invalid grant" or "Token expired"

**Cause:** Token needs refresh

**Solution:**
```bash
# Delete old token
rm credentials/token.json

# Login again in the app
# Click "Login with Google"
```

---

### Issue 5: "Module not found" errors

**Cause:** Missing dependencies

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

---

### Issue 6: "Model not found"

**Cause:** Spam classifier model not trained

**Solution:**
```bash
python train_model.py
```

---

### Issue 7: Port 8501 already in use

**Cause:** Another Streamlit app running

**Solution:**
```bash
# Use different port:
streamlit run app.py --server.port 8502
```

---

## 📊 Testing the Integration

### Test Checklist

- [ ] Google Cloud project created
- [ ] Gmail API enabled
- [ ] OAuth consent screen configured
- [ ] Test user added (your email)
- [ ] OAuth credentials downloaded
- [ ] `credentials.json` in correct folder
- [ ] Dependencies installed
- [ ] Model trained (model.pkl exists)
- [ ] App runs (`streamlit run app.py`)
- [ ] Login successful
- [ ] Emails fetched and displayed
- [ ] Spam predictions working
- [ ] Can export CSV results

---

## 🎯 Usage Tips

### Scanning Emails

- **First Scan:** May take 10-15 seconds
- **Subsequent Scans:** 5-10 seconds
- **Default Limit:** 20 most recent emails
- **Change Limit:** Edit `config.py` → `MAX_EMAILS`

### Interpreting Results

- **Spam:** Confidence >70% = High confidence
- **Ham:** Confidence >80% = Very reliable
- **Low Confidence:** Manual review recommended

### Privacy

- **Local Processing:** All ML predictions happen locally
- **No Data Sent:** Emails stay on your machine
- **Token Storage:** Encrypted, stored locally
- **Revoke Access:** Delete `token.json` or revoke in Google Account settings

---

## 🔄 Updating the App

To get latest features:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
streamlit run app.py
```

---

## 🌐 Deploying to Cloud (Optional)

### Streamlit Cloud

**Note:** Cannot deploy with Gmail OAuth to Streamlit Cloud's free tier due to redirect URL restrictions.

**Alternatives:**
1. **Run Locally:** Best option for Gmail integration
2. **Self-Host:** Deploy on your own server
3. **Use Service Account:** For organization-wide deployment

---

## 🆘 Getting More Help

### Resources

- **Google Cloud Docs:** https://cloud.google.com/docs
- **Gmail API Docs:** https://developers.google.com/gmail/api
- **Streamlit Docs:** https://docs.streamlit.io

### Support

- Open an issue on GitHub
- Check existing issues for solutions
- Contact project maintainer

---

## ✅ Setup Complete!

You now have a fully functional Gmail spam classifier! 🎉

**Next Steps:**
1. Scan your inbox
2. Review spam predictions
3. Export results
4. Customize settings in `config.py`
5. Add more features!

---

**Security Reminder:**
- Never share your `credentials.json`
- Never commit OAuth files to Git
- Revoke access when no longer needed
- Use strong Google account password

---

**Happy Spam Detecting! 📧🚫**