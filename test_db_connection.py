from database import get_db_connection, init_db

def test_connection():
    try:
        print("Connecting to SQLite Cloud...")
        db = get_db_connection()
        print("Successfully connected to SQLite Cloud")
        
        print("Initializing database tables...")
        init_db(db)
        print("Successfully initialized database tables")
        
        print("Testing query execution...")
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Available tables:", [table['name'] for table in tables])
        
        db.close()
        print("Connection test completed successfully")
        
    except Exception as e:
        print(f"Error during database test: {e}")

if __name__ == "__main__":
    test_connection()
