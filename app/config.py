import os
from dotenv import load_dotenv

# Load .env file on startup
load_dotenv()

def get_secret(secret_name):
    return os.getenv(secret_name)
