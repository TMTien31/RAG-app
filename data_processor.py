import pandas as pd
import numpy as np
import ast
from typing import Any, List, Union

class DataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_csv(file_path)

    def get_data(self):
        return self.df
    
    def save_data(self, output_path=None):
        """Save the processed data."""
        records = self.df.to_dict(orient="records")
        
        # If output path provided, save to file
        if output_path:
            # You could save as JSON, CSV, or another format
            self.df.to_csv(output_path, index=False)

    def process_data(self):
        """Process the DataFrame by cleaning up and formatting columns."""
        # Replace infinities with None
        self.df = self.df.replace([float("inf"), float("-inf")], None)
        
        # Process color_options column safely
        self.df["color_options"] = self.df.apply(self._process_color_options, axis=1)
        
        return self.df
    
    def _process_color_options(self, row):
        """Safely process a single value in the color_options column."""
        value = row["color_options"]
        
        # Handle NaN/None
        if pd.isna(value):
            return None
            
        # Convert string representation of list to actual list
        if isinstance(value, str):
            try:
                if value.strip().startswith('[') and value.strip().endswith(']'):
                    value = ast.literal_eval(value)
                else:
                    # If it's not a list representation, return as is
                    return value
            except (SyntaxError, ValueError):
                # If parsing fails, return the original string
                return value
        
        # Handle different types of iterables (lists, tuples, numpy arrays)
        if isinstance(value, (list, tuple)):
            # Convert all items to strings and join
            return ", ".join(str(item) for item in value)
        elif isinstance(value, np.ndarray):
            # Flatten and convert numpy array items to strings
            return ", ".join(str(item) for item in value.flatten())
        
        # Return as is for other types
        return value

    def save_data(self, output_path=None):
        """Save the processed data."""
        records = self.df.to_dict(orient="records")
        
        # If output path provided, save to file
        if output_path:
            # You could save as JSON, CSV, or another format
            self.df.to_csv(output_path, index=False)
            
        return records

    def embed_data(self, column_name, embedding_model):
        """Generate embeddings for the specified column."""
        # Make sure the column exists
        if column_name not in self.df.columns:
            raise ValueError(f"Column '{column_name}' not found in DataFrame")
            
        # Apply the embedding model to generate embeddings
        self.df["embedding"] = self.df[column_name].apply(
            lambda x: embedding_model.encode(str(x)) if pd.notna(x) else None
        )
        
        return self.df
    
    def save_data_to_db(self, vector_db, db_name, collection_name):
        records = self.df.to_dict(orient="records")
        for i, record in enumerate(records):
            # Check if embeddings are in the record
            if 'embedding' not in record:
                raise ValueError("Data must contain 'embedding' field. Please run embed_data() first.")
            
            # Format the data for Qdrant
            item = {
                "id": i + 1,  # Use integer ID starting from 1
                "vector": record['embedding'],
                "payload": {k: v for k, v in record.items() if k != 'embedding'}
            }
            
            # Call add_item with the parameters it expects
            vector_db.add_item(
                data=item,
                db_name=db_name,
                collection_name=collection_name
            )
