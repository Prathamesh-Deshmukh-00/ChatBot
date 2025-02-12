import os
from dotenv import load_dotenv
import google.generativeai as genai
import mysql.connector

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in environment variables!")

genai.configure(api_key=api_key)

def get_gemini_model():
    """Returns the Gemini AI model."""
    return genai.GenerativeModel("gemini-1.5-flash")

def get_db_connection():
    """Connects to the MySQL database."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )
