from pymongo import MongoClient
import os
import dotenv

dotenv.load_dotenv()

# Replace with your MongoDB Atlas URI
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]
