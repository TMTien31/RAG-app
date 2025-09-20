from vector_db import VectorDatabase
from data_processor import DataProcessor
from embeddings import Embeddings

def main():
    print("Starting RAG...")
    print("Initializing Vector Database...")
    qdrant_db = VectorDatabase("qdrant")

    print("Initializing Data Processor...")
    data_processor = DataProcessor(
        file_path="./hoanghamobile.csv"
    )

    print("Initializing Embeddings...")
    embeddings = Embeddings(
        model_name="gemini-embedding-001",
        type="gemini"
    )
    
    print("Processing Data...")
    data_processor.process_data()
    
    print("Embedding Data...")
    data_processor.embed_data(
        column_name="title",
        embedding_model=embeddings
    )

    print("Getting Data...")
    data = data_processor.get_data()

    print("processed_data", data.head())

    # Clean up data
    print("Cleaning up data...")
    qdrant_db.clear_collection("products")

    print("Saving Data to Database...")
    data_processor.save_data_to_db(
        vector_db=qdrant_db,
        db_name="hoanghamobile",
        collection_name="products"
    )

    print("Testing Search...")


    query = "vivo"
    query_vector = embeddings.encode(query)
    result = qdrant_db.search(
        query_vector=query_vector,
        collection_name="products",
        limit=5  # Get top 5 results
    )

    # Print the highest scoring result
    if result:
        print("Top result:", result[0])
        print("Score:", result[0]["score"])
        print("Title:", result[0]["payload"].get("title", "No title"))
    else:
        print("No results found")



if __name__ == "__main__":
    main()
