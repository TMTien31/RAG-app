from pymongo import MongoClient
from chromadb import HttpClient
from qdrant_client import QdrantClient
from qdrant_client import models as qdrant_models
import os
from dotenv import load_dotenv

load_dotenv()
class VectorDatabase:
    def __init__(self, db_type):
        self.db_type = db_type

        if db_type == "mongodb":
            self.client = MongoClient(os.getenv("MONGODB_URI"))
            self.ping()

        elif db_type == "chromadb":
            self.client = HttpClient(
                host="localhost", 
                port=8000
            )
            self.ping()

        elif db_type == "qdrant":
            self.client = QdrantClient(
                url=os.getenv("QDRANT_URL"),
                api_key=os.getenv("QDRANT_KEY"),
            )
            self.ping()

    def add_item(self, data, db_name, collection_name):
        if self.db_type == "qdrant":
            # Prepare point data for Qdrant
            point_id = data.get("id")
            vector = data.get("vector")
            payload = data.get("payload", {})
            
            if not point_id or not vector:
                raise ValueError("Data must contain 'id' and 'vector' fields for Qdrant")
            
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            if collection_name not in collection_names:
                try:
                    self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config=qdrant_models.VectorParams(
                            size=1536,
                            distance=qdrant_models.Distance.COSINE
                        )
                    )
                    print(f"Created collection '{collection_name}' in Qdrant")
                except Exception as e:
                    print(f"Failed to create collection: {str(e)}")

            result = self.client.upsert(
                collection_name=collection_name,
                points=[
                    qdrant_models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload
                    )
                ]
            )
            return {"success": True, "operation": "upsert", "collection": collection_name}
        else:
            print("TODO: Need to implement...")
    
    def clear_collection(self, collection_name):
        if self.db_type == "qdrant":
            self.client.delete_collection(collection_name=collection_name)
        else:
            print("TODO: Need to implement...")

    def search(self, query_vector, collection_name, limit=5):
        if self.db_type == "qdrant":
            # Perform the search
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            # Extract the results
            results = []
            for res in search_result:
                result = {
                    "id": res.id,
                    "score": res.score,  # This is the similarity score
                    "payload": res.payload
                }
                results.append(result)
            
            # Sort by score to get highest scores first
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results
        else:
            print("TODO: Need to implement...")
            return []
    
    def ping(self):
        """Check if the database is alive and responsive"""
        try:
            
            if self.db_type == "mongodb":
                # MongoDB has a command_cursor ping
                result = self.client.admin.command('ping')
                if result.get('ok') == 1.0:
                    print("MongoDB connection successful")
                else:
                    print("MongoDB ping failed")
                
            elif self.db_type == "chromadb":
                # ChromaDB doesn't have a direct ping, but we can list collections
                self.client.list_collections()
                print("ChromaDB connection successful")
                
            elif self.db_type == "qdrant":
                # For Qdrant client v1.14.2, use get_collections() instead of health()
                try:
                    # Get the list of collections
                    collections = self.client.get_collections()
                    # If we get here without exception, the connection is working
                    print(f"Qdrant connection successful. Found {len(collections.collections)} collections.")
                    return True, f"Qdrant connection successful. Found {len(collections.collections)} collections."
                except Exception as e:
                    # If we can't get collections, try a simpler healthcheck
                    try:
                        # Some versions have a healthcheck method called get_cluster_info
                        cluster_info = self.client.cluster_info()
                        print("Qdrant connection successful (verified via cluster_info)")
                        return True, "Qdrant connection successful"
                    except Exception as e2:
                        print(f"Qdrant connection failed: {str(e2)}")
                        return False, f"Qdrant connection failed: {str(e2)}"
                
            else:
                print(f"Unknown database type: {self.db_type}")
                
        except Exception as e:
            print(f"{self.db_type} connection failed: {str(e)}")