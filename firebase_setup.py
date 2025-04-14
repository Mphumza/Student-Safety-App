import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
import requests
import base64

# Get Firebase credentials from environment variable
firebase_json = os.environ.get("FIREBASE_CREDENTIALS")

if not firebase_json:
    raise ValueError("Missing FIREBASE_CREDENTIALS environment variable")

# Firebase Admin SDK setup for backend operations (Firestore)
cred = credentials.Certificate(json.loads(firebase_json))
firebase_admin.initialize_app(cred)

# Firestore setup
db = firestore.client()

# Firebase config for Pyrebase (authentication)
firebaseConfig = {
  "apiKey": "AIzaSyC4du9PpLM6IYTmpzTHT--yWVZdRHB1GEE",
  "authDomain": "studenttracker2-82547.firebaseapp.com",
  "projectId": "studenttracker2-82547",
  "storageBucket": "studenttracker2-82547.firebasestorage.app",
  "messagingSenderId": "881424394419",
  "appId": "1:881424394419:web:3669f4bdb83e4479f0a8c6",
  "databaseURL": "https://studenttracker2-82547.firebaseio.com",
  "measurementId": "G-STNFFEH210"
}

IMGBB_API_KEY = '3adaa8e4932309a2251dd119a5d28754'

def upload_image_to_imgbb(image_file):
    """Uploads image to imgbb and returns the image URL."""
    
    # Read the image file and encode it to base64
    image_data = base64.b64encode(image_file.read()).decode("utf-8")

    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": image_data,
        "name": image_file.filename
    }

    response = requests.post(url, data=payload)
    response.raise_for_status()

    image_url = response.json()['data']['url']
    return image_url

# Initialize Pyrebase for handling authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
