# Firebase Integration Guide

This guide explains how to add your Google Firebase project to the RPR CIS Dashboard.

## Prerequisites

1. A Google account
2. A Firebase project (create one at [Firebase Console](https://console.firebase.google.com/))
3. Python 3.8+

## Step 1: Create a Firebase Project

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"** or **"Create a project"**
3. Enter your project name (e.g., "rpr-cis-dashboard")
4. Choose whether to enable Google Analytics (optional)
5. Click **"Create project"**

## Step 2: Generate Service Account Credentials

1. In Firebase Console, go to **Project Settings** (gear icon)
2. Navigate to the **"Service accounts"** tab
3. Click **"Generate new private key"**
4. Save the downloaded JSON file as `firebase-credentials.json` in the project root
5. **Important:** Add this file to `.gitignore` to keep credentials secure

## Step 3: Install Firebase Admin SDK

Add the Firebase Admin SDK to your requirements:

```bash
pip install firebase-admin
```

Or add to `requirements.txt`:
```
firebase-admin
```

## Step 4: Configure Firebase in the Application

Create a new configuration file `src/firebase_config.py`:

```python
"""
Firebase Configuration Module
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Path to your Firebase service account key
FIREBASE_CREDENTIALS_PATH = os.environ.get(
    'FIREBASE_CREDENTIALS_PATH',
    'firebase-credentials.json'
)

# Initialize Firebase (call once at app startup)
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'your-project-id.appspot.com'  # Replace with your bucket
        })
    return firebase_admin.get_app()

# Get Firestore client
def get_firestore_client():
    """Get Firestore database client"""
    initialize_firebase()
    return firestore.client()

# Get Storage client
def get_storage_bucket():
    """Get Firebase Storage bucket"""
    initialize_firebase()
    return storage.bucket()
```

## Step 5: Update Environment Variables

Create a `.env` file (add to `.gitignore`):

```env
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

## Step 6: Integrate Firebase into the Application

### Option A: Use Firestore Instead of SQLite

Update `src/database.py` to use Firestore:

```python
"""
Firebase Firestore Database Module
"""

from firebase_config import get_firestore_client
from datetime import datetime
from typing import Dict, List

class FirestoreDatabase:
    """
    Firestore database handler for CIS Dashboard
    """
    
    def __init__(self):
        self.db = get_firestore_client()
    
    def save_verification(self, verification: Dict):
        """Save verification record to Firestore"""
        doc_ref = self.db.collection('verifications').document(verification['id'])
        verification['updated_at'] = datetime.utcnow().isoformat()
        doc_ref.set(verification)
    
    def get_verification(self, verification_id: str) -> Dict:
        """Get verification by ID"""
        doc_ref = self.db.collection('verifications').document(verification_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def save_dispute(self, dispute: Dict):
        """Save dispute record to Firestore"""
        doc_ref = self.db.collection('disputes').document(dispute['id'])
        dispute['updated_at'] = datetime.utcnow().isoformat()
        doc_ref.set(dispute)
    
    def get_dispute(self, dispute_id: str) -> Dict:
        """Get dispute by ID"""
        doc_ref = self.db.collection('disputes').document(dispute_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def get_all_disputes(self) -> List[Dict]:
        """Get all disputes"""
        disputes_ref = self.db.collection('disputes')
        return [doc.to_dict() for doc in disputes_ref.stream()]
    
    def save_audit_entry(self, entity_type: str, entity_id: str, action: str, 
                        details: Dict, user_id: str = None):
        """Save audit trail entry to Firestore"""
        audit_ref = self.db.collection('audit_trail')
        audit_ref.add({
            'entity_type': entity_type,
            'entity_id': entity_id,
            'action': action,
            'details': details,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        })
```

### Option B: Use Firebase Storage for Documents

Update document upload handling to use Firebase Storage:

```python
"""
Firebase Storage Module
"""

from firebase_config import get_storage_bucket
import os

def upload_document_to_firebase(local_path: str, destination_path: str = None) -> str:
    """
    Upload a document to Firebase Storage
    
    Args:
        local_path: Path to local file
        destination_path: Path in Firebase Storage (optional)
    
    Returns:
        Public URL of uploaded file
    """
    bucket = get_storage_bucket()
    
    if destination_path is None:
        destination_path = f"documents/{os.path.basename(local_path)}"
    
    blob = bucket.blob(destination_path)
    blob.upload_from_filename(local_path)
    
    # Make the file publicly accessible (optional)
    blob.make_public()
    
    return blob.public_url

def download_document_from_firebase(firebase_path: str, local_path: str):
    """
    Download a document from Firebase Storage
    
    Args:
        firebase_path: Path in Firebase Storage
        local_path: Local destination path
    """
    bucket = get_storage_bucket()
    blob = bucket.blob(firebase_path)
    blob.download_to_filename(local_path)
```

### Option C: Use Firebase Authentication

Enable Firebase Auth in your Flask app:

```python
"""
Firebase Authentication Module
"""

from firebase_admin import auth
from functools import wraps
from flask import request, jsonify

def verify_firebase_token(id_token: str) -> dict:
    """Verify Firebase ID token"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise ValueError(f"Invalid token: {str(e)}")

def firebase_auth_required(f):
    """Decorator to require Firebase authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.split('Bearer ')[1]
        
        try:
            decoded_token = verify_firebase_token(token)
            request.user = decoded_token
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': str(e)}), 401
    
    return decorated_function
```

## Step 7: Update Flask App

In `ui/app.py`, initialize Firebase at startup:

```python
# Add at the top of the file
from firebase_config import initialize_firebase

# Initialize Firebase before other components
initialize_firebase()
```

## Security Best Practices

1. **Never commit credentials to Git**
   - Add `firebase-credentials.json` to `.gitignore`
   - Use environment variables for sensitive data

2. **Set up Firestore Security Rules**
   ```
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /verifications/{docId} {
         allow read, write: if request.auth != null;
       }
       match /disputes/{docId} {
         allow read, write: if request.auth != null;
       }
       match /audit_trail/{docId} {
         allow read: if request.auth != null;
         allow write: if request.auth != null;
       }
     }
   }
   ```

3. **Set up Storage Security Rules**
   ```
   rules_version = '2';
   service firebase.storage {
     match /b/{bucket}/o {
       match /documents/{allPaths=**} {
         allow read, write: if request.auth != null;
       }
     }
   }
   ```

## Environment Configuration Summary

| Variable | Description | Example |
|----------|-------------|---------|
| `FIREBASE_CREDENTIALS_PATH` | Path to service account JSON | `firebase-credentials.json` |
| `FIREBASE_PROJECT_ID` | Your Firebase project ID | `my-project-123` |
| `FIREBASE_STORAGE_BUCKET` | Storage bucket name | `my-project-123.appspot.com` |

## Troubleshooting

### Common Issues

1. **"Could not load the default credentials"**
   - Ensure `firebase-credentials.json` exists and path is correct
   - Check `FIREBASE_CREDENTIALS_PATH` environment variable

2. **"Permission denied" errors**
   - Verify Firestore/Storage security rules
   - Ensure the service account has required permissions

3. **"Project not found"**
   - Verify project ID matches your Firebase project
   - Check that Firestore/Storage is enabled in Firebase Console

## Additional Resources

- [Firebase Admin SDK Documentation](https://firebase.google.com/docs/admin/setup)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Storage Documentation](https://firebase.google.com/docs/storage)
- [Firebase Authentication Documentation](https://firebase.google.com/docs/auth)
