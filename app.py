from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
from contextlib import contextmanager
import os
from datetime import datetime
import random
import string

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Ajay@070804'),
    'database': os.getenv('DB_NAME', 'BooksDB'),
    # allow an explicit port (useful on cloud providers)
    'port': int(os.getenv('DB_PORT', '3306'))
}

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    try:
        yield cursor, conn
    finally:
        cursor.close()
        conn.close()

def generate_author_id():
    """Generate a unique author ID in format XXX-XX-XXXX"""
    return f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"

def generate_title_id():
    """Generate a unique title ID in format LLNNNN"""
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=4))
    return letters + numbers

# ==================== MAIN PAGE ====================

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

# ==================== AUTHOR ENDPOINTS ====================

@app.route('/api/authors', methods=['GET'])
def get_authors():
    """Get all authors"""
    try:
        with get_db_connection() as (cursor, conn):
            cursor.execute("""
                SELECT au_id, au_name, au_fname, phone, address, city, state, zip, contract 
                FROM authors 
                ORDER BY au_id ASC
            """)
            authors = cursor.fetchall()
            return jsonify({'success': True, 'data': authors})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/authors', methods=['POST'])
def add_author():
    """Add a new author"""
    try:
        data = request.json
        au_name = data.get('au_name', '').strip()
        au_fname = data.get('au_fname', '').strip() or None
        phone = data.get('phone', '').strip() or None
        address = data.get('address', '').strip() or None
        city = data.get('city', '').strip() or None
        state = data.get('state', '').strip() or None
        zip_code = data.get('zip', '').strip() or None
        contract = data.get('contract', False)
        
        if not au_name:
            return jsonify({'success': False, 'error': 'Author last name is required'}), 400
        
        # Generate unique author ID
        au_id = generate_author_id()
        
        with get_db_connection() as (cursor, conn):
            cursor.execute("""
                INSERT INTO authors (au_id, au_name, au_fname, phone, address, city, state, zip, contract)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (au_id, au_name, au_fname, phone, address, city, state, zip_code, contract))
            conn.commit()
            return jsonify({'success': True, 'message': 'Author added successfully', 'id': au_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/authors/<au_id>', methods=['GET'])
def get_author(au_id):
    """Get a specific author"""
    try:
        with get_db_connection() as (cursor, conn):
            cursor.execute("""
                SELECT au_id, au_name, au_fname, phone, address, city, state, zip, contract 
                FROM authors 
                WHERE au_id = %s
            """, (au_id,))
            author = cursor.fetchone()
            
            if not author:
                return jsonify({'success': False, 'error': 'Author not found'}), 404
            
            return jsonify({'success': True, 'data': author})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/authors/<au_id>', methods=['PUT'])
def update_author(au_id):
    """Update an existing author"""
    try:
        data = request.json
        au_name = data.get('au_name', '').strip()
        au_fname = data.get('au_fname', '').strip() or None
        phone = data.get('phone', '').strip() or None
        address = data.get('address', '').strip() or None
        city = data.get('city', '').strip() or None
        state = data.get('state', '').strip() or None
        zip_code = data.get('zip', '').strip() or None
        contract = data.get('contract', False)
        
        if not au_name:
            return jsonify({'success': False, 'error': 'Author last name is required'}), 400
        
        with get_db_connection() as (cursor, conn):
            cursor.execute("""
                UPDATE authors 
                SET au_name=%s, au_fname=%s, phone=%s, address=%s, city=%s, state=%s, zip=%s, contract=%s
                WHERE au_id=%s
            """, (au_name, au_fname, phone, address, city, state, zip_code, contract, au_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'Author updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/authors/<au_id>', methods=['DELETE'])
def delete_author(au_id):
    """Delete an author and their orphaned books"""
    try:
        with get_db_connection() as (cursor, conn):
            # Get all books by this author
            cursor.execute("""
                SELECT DISTINCT title_id FROM titleauthor WHERE au_id = %s
            """, (au_id,))
            book_ids = [row['title_id'] for row in cursor.fetchall()]
            
            # Find books that will become orphaned
            books_to_delete = []
            for book_id in book_ids:
                cursor.execute("SELECT COUNT(*) as count FROM titleauthor WHERE title_id = %s", (book_id,))
                count = cursor.fetchone()['count']
                if count == 1:
                    books_to_delete.append(book_id)
            
            # Delete relationships
            cursor.execute("DELETE FROM titleauthor WHERE au_id = %s", (au_id,))
            
            # Delete orphaned books
            for book_id in books_to_delete:
                cursor.execute("DELETE FROM titles WHERE title_id = %s", (book_id,))
            
            # Delete author
            cursor.execute("DELETE FROM authors WHERE au_id = %s", (au_id,))
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': f'Author deleted. {len(books_to_delete)} book(s) removed.'
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== TITLE ENDPOINTS ====================

@app.route('/api/titles', methods=['GET'])
def get_titles():
    """Get all titles with their authors"""
    try:
        with get_db_connection() as (cursor, conn):
            cursor.execute("""
                SELECT 
                    t.title_id,
                    t.title,
                    t.type,
                    t.pub_id,
                    t.price,
                    t.advance,
                    t.royalty,
                    t.ytd_sales,
                    t.notes,
                    t.pubdate,
                    GROUP_CONCAT(CONCAT(a.au_fname, ' ', a.au_name) SEPARATOR ', ') as authors,
                    GROUP_CONCAT(a.au_id SEPARATOR ',') as author_ids
                FROM titles t
                LEFT JOIN titleauthor ta ON t.title_id = ta.title_id
                LEFT JOIN authors a ON ta.au_id = a.au_id
                GROUP BY t.title_id
                ORDER BY t.title_id ASC
            """)
            titles = cursor.fetchall()
            
            # Convert date to display string (DD-MM-YYYY)
            for title in titles:
                if title['pubdate']:
                    title['pubdate'] = title['pubdate'].strftime('%d-%m-%Y')
            
            return jsonify({'success': True, 'data': titles})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/titles', methods=['POST'])
def add_title():
    """Add a new title"""
    try:
        data = request.json
        title = data.get('title', '').strip()
        type_val = data.get('type', '').strip() or None
        pub_id = data.get('pub_id', '').strip() or None
        price = data.get('price', '')
        advance = data.get('advance', '')
        royalty = data.get('royalty', '')
        ytd_sales = data.get('ytd_sales', '')
        notes = data.get('notes', '').strip() or None
        pubdate = data.get('pubdate', '').strip() or None
        author_id = data.get('author_id')
        royaltyper = data.get('royaltyper', 100)
        
        if not title or not author_id:
            return jsonify({'success': False, 'error': 'Title and author are required'}), 400
        
        # Convert values
        price_val = float(price) if price else None
        advance_val = float(advance) if advance else None
        royalty_val = int(royalty) if royalty else None
        ytd_sales_val = int(ytd_sales) if ytd_sales else None
        
        # Normalize incoming pubdate to ISO (YYYY-MM-DD) so MySQL accepts it.
        if pubdate:
            # Accept either YYYY-MM-DD or DD-MM-YYYY from the client
            for fmt in ('%Y-%m-%d', '%d-%m-%Y'):
                try:
                    parsed = datetime.strptime(pubdate, fmt).date()
                    pubdate = parsed.strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue

        # Generate unique title ID
        title_id = generate_title_id()
        
        with get_db_connection() as (cursor, conn):
            cursor.execute("""
                INSERT INTO titles (title_id, title, type, pub_id, price, advance, royalty, ytd_sales, notes, pubdate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (title_id, title, type_val, pub_id, price_val, advance_val, royalty_val, ytd_sales_val, notes, pubdate))
            
            # Link to author
            cursor.execute("""
                INSERT INTO titleauthor (au_id, title_id, au_ord, royaltyper)
                VALUES (%s, %s, 1, %s)
            """, (author_id, title_id, royaltyper))
            
            conn.commit()
            return jsonify({'success': True, 'message': 'Title added successfully', 'id': title_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/titles/<title_id>', methods=['GET'])
def get_title(title_id):
    """Get a specific title with its authors"""
    try:
        with get_db_connection() as (cursor, conn):
            cursor.execute("""
                SELECT title_id, title, type, pub_id, price, advance, royalty, ytd_sales, notes, pubdate
                FROM titles 
                WHERE title_id = %s
            """, (title_id,))
            title = cursor.fetchone()
            
            if not title:
                return jsonify({'success': False, 'error': 'Title not found'}), 404
            
            # Convert date to display string (DD-MM-YYYY)
            if title['pubdate']:
                title['pubdate'] = title['pubdate'].strftime('%d-%m-%Y')
            
            # Get authors
            cursor.execute("""
                SELECT a.au_id, a.au_name, a.au_fname, ta.au_ord, ta.royaltyper
                FROM authors a
                JOIN titleauthor ta ON a.au_id = ta.au_id
                WHERE ta.title_id = %s
                ORDER BY ta.au_ord
            """, (title_id,))
            title['authors'] = cursor.fetchall()
            
            return jsonify({'success': True, 'data': title})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/titles/<title_id>', methods=['PUT'])
def update_title(title_id):
    """Update an existing title"""
    try:
        data = request.json
        title = data.get('title', '').strip()
        type_val = data.get('type', '').strip() or None
        pub_id = data.get('pub_id', '').strip() or None
        price = data.get('price', '')
        advance = data.get('advance', '')
        royalty = data.get('royalty', '')
        ytd_sales = data.get('ytd_sales', '')
        notes = data.get('notes', '').strip() or None
        pubdate = data.get('pubdate', '').strip() or None
        authors = data.get('authors', [])  # List of {au_id, royaltyper}
        
        if not title:
            return jsonify({'success': False, 'error': 'Title is required'}), 400
        
        # Convert values
        price_val = float(price) if price else None
        advance_val = float(advance) if advance else None
        royalty_val = int(royalty) if royalty else None
        ytd_sales_val = int(ytd_sales) if ytd_sales else None
        
        with get_db_connection() as (cursor, conn):
            cursor.execute("""
                UPDATE titles 
                SET title=%s, type=%s, pub_id=%s, price=%s, advance=%s, royalty=%s, ytd_sales=%s, notes=%s, pubdate=%s
                WHERE title_id=%s
            """, (title, type_val, pub_id, price_val, advance_val, royalty_val, ytd_sales_val, notes, pubdate, title_id))
            
            # Update author links
            cursor.execute("DELETE FROM titleauthor WHERE title_id = %s", (title_id,))
            for idx, author in enumerate(authors, 1):
                cursor.execute("""
                    INSERT INTO titleauthor (au_id, title_id, au_ord, royaltyper)
                    VALUES (%s, %s, %s, %s)
                """, (author['au_id'], title_id, idx, author.get('royaltyper', 100)))
            
            conn.commit()
            return jsonify({'success': True, 'message': 'Title updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/titles/<title_id>', methods=['DELETE'])
def delete_title(title_id):
    """Delete a title"""
    try:
        with get_db_connection() as (cursor, conn):
            cursor.execute("DELETE FROM titleauthor WHERE title_id = %s", (title_id,))
            cursor.execute("DELETE FROM titles WHERE title_id = %s", (title_id,))
            conn.commit()
            return jsonify({'success': True, 'message': 'Title deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/titles/by-author/<au_id>', methods=['GET'])
def get_titles_by_author(au_id):
    """Get all titles by a specific author"""
    try:
        with get_db_connection() as (cursor, conn):
            cursor.execute("""
                SELECT t.title_id, t.title, t.type, t.price, t.pubdate, ta.royaltyper
                FROM titles t
                JOIN titleauthor ta ON t.title_id = ta.title_id
                WHERE ta.au_id = %s
                ORDER BY t.title_id ASC
            """, (au_id,))
            titles = cursor.fetchall()
            
            # Convert dates to display string (DD-MM-YYYY)
            for title in titles:
                if title['pubdate']:
                    title['pubdate'] = title['pubdate'].strftime('%d-%m-%Y')
            
            return jsonify({'success': True, 'data': titles})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if the API and database are working"""
    try:
        with get_db_connection() as (cursor, conn):
            cursor.execute("SELECT 1")
            return jsonify({'success': True, 'message': 'API and database are healthy'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
