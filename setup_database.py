import mysql.connector

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Ajay@070804',
    'database': 'BooksDB'
}

def setup_database():
    """Set up the database with the new schema automatically"""
    try:
        print("Connecting to database...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Reading schema.sql...")
        with open('schema.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("Executing SQL statements...")
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        
        for i, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
                print(f"  ✓ Statement {i}/{len(statements)}")
            except Exception as e:
                print(f"  ✗ Error in statement {i}: {e}")
        
        conn.commit()
        
        # Show counts
        cursor.execute("SELECT COUNT(*) FROM authors")
        author_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM titles")
        title_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM titleauthor")
        relation_count = cursor.fetchone()[0]
        
        print(f"\n✓ Setup complete!")
        print(f"  - {author_count} authors")
        print(f"  - {title_count} titles")
        print(f"  - {relation_count} relationships")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == '__main__':
    setup_database()
