from vector_db import VectorDatabase

class VectorSearch:
    def __init__(self, db_type):
        self.db_type = db_type
        if db_type == "mongodb":
            self.client = VectorDatabase("mongodb")
        elif db_type == "chromadb":
            self.client = VectorDatabase("chromadb")
        elif db_type == "qdrant":
            self.client = VectorDatabase("qdrant")


