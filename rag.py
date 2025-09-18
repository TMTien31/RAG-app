from vector_db import VectorDatabase

def main():
    db = VectorDatabase(db_type="qdrant")
    print(f"Connected to {db.db_type} database.")

if __name__ == "__main__":
    main()