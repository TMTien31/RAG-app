import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from google import genai


load_dotenv()

class Embeddings:
    def __init__(self, model_name, type):
        self.model_name = model_name
        self.type = type
        if type == "sentence_transformers":
            self.client = SentenceTransformer(model_name)
        elif type == "gemini":
            self.client = genai.Client(
                api_key=os.getenv("GEMINI_API")
            )

    def encode(self, doc):
        if self.type == "sentence_transformers":
            return self.client.encode(doc)
        elif self.type == "gemini":
            return self.client.models.embed_content(
                model=self.model_name,
                contents=doc
            ).embeddings[0].values
        

        
