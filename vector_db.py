from pymongo import MongoClient
from chromadb import HttpClient
from qdrant_client import QdrantClient
from qdrant_client import models as qdrant_models
from supabase import create_client, Client

from dotenv import load_dotenv
import os

load_dotenv()

class VectorDatabase:
    def __init__(self, db_type: str):
        self.db_type = db_type
        if self.db_type == "mongodb":
            self.client = MongoClient(os.getenv("MONGO_URI"))
        elif self.db_type == "chromadb":
            self.client = HttpClient(
                host="localhost", 
                port=8123
            )
        elif self.db_type == "qdrant":
            self.client = QdrantClient(
                url=os.getenv("QDRANT_URL"),
                api_key=os.getenv("QDRANT_KEY"),
            )
        elif self.db_type == "supabase":
            self.client = create_client(
                supabase_url=os.environ.get("SUPABASE_URL"),
                supabase_key=os.environ.get("SUPABASE_KEY")
            )