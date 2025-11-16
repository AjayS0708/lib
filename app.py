from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
import random
import string
from dotenv import load_dotenv
from whitenoise import WhiteNoise

app = Flask(__name__, static_folder='static')
CORS(app)

# Configure Whitenoise for static files
app.wsgi_app = WhiteNoise(
    app.wsgi_app,
    root='static/',
    prefix='static/',
    index_file=True
)

# Load environment variables
load_dotenv()

# MongoDB connection - Lazy initialization to allow app to start even if DB is temporarily unavailable
MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'BooksDB')

# Global variables for MongoDB connection
client = None
db = None
authors_collection = None
titles_collection = None

def init_mongodb():
    """Initialize MongoDB connection - called on first request"""
    global client, db, authors_collection, titles_collection
    
    if client is not None:
        return  # Already initialized
    
    try:
        # Ensure connection string has proper parameters for MongoDB Atlas
        connection_uri = MONGO_URI
        
        # Parse the connection string
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        # Parse the URI
        parsed = urlparse(connection_uri)
        query = parse_qs(parsed.query)
        
        # Add required parameters
        query['retryWrites'] = 'true'
        query['w'] = 'majority'
        
        # For MongoDB Atlas, we need to use tls/ssl
        if 'ssl' not in query:
            query['ssl'] = 'true'
            
        # Rebuild the query string
        new_query = urlencode(query, doseq=True)
        
        # Rebuild the URI
        connection_uri = urlunparse(parsed._replace(query=new_query))
        
        print(f"Connecting to MongoDB with URI: {connection_uri.replace(parsed.password, '***') if parsed.password else connection_uri}")
        
        # Configure the client with SSL and other options
        client = MongoClient(
            connection_uri,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=10000,         # 10 second connection timeout
            socketTimeoutMS=45000,          # 45 second socket timeout
            maxPoolSize=50,                 # Connection pool size
            tls=True,                       # Enable TLS
            tlsAllowInvalidCertificates=False,
            retryWrites=True,
            appname='books-manager-app'     # Identify this connection in MongoDB logs
        )
        
        # Test connection
        client.admin.command('ping')
        db = client[DB_NAME]
        authors_collection = db['authors']
        titles_collection = db['titles']
        print(f"✅ Successfully connected to MongoDB database: {DB_NAME}")
    except Exception as e:
        print(f"❌ MongoDB connection error: {str(e)}")
        print("⚠️  Make sure MONGODB_URI is set correctly in environment variables")
        print("⚠️  Check MongoDB Atlas Network Access allows connections from Render (0.0.0.0/0)")
        print("⚠️  IMPORTANT: Set Python version to 3.11 in Render dashboard (Settings → Environment)")
        raise

# Helper function to ensure MongoDB is initialized
def ensure_db():
    """Ensure MongoDB connection is initialized"""
    global client, db, authors_collection, titles_collection
    if client is None or db is None:
        init_mongodb()
    return db, authors_collection, titles_collection

# Try to initialize on import, but don't crash if it fails
try:
    init_mongodb()
except Exception as e:
    print("⚠️  MongoDB connection will be retried on first request")
    # Don't raise - allow app to start

def generate_author_id():
    """Generate a unique author ID in format XXX-XX-XXXX"""
    return f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"

def generate_title_id():
    """Generate a unique title ID in format LLNNNN"""
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=4))
    return letters + numbers

def serialize_objectid(obj):
    """Recursively convert ObjectId instances to strings in dictionaries and lists"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: serialize_objectid(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_objectid(item) for item in obj]
    else:
        return obj

# ==================== MAIN PAGE ====================

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

# ==================== AUTHOR ENDPOINTS ====================

def serialize_author(author):
    """Convert MongoDB document to JSON serializable format"""
    if not author:
        return None
    author['_id'] = str(author['_id'])  # Convert ObjectId to string
    return author

@app.route('/api/authors', methods=['GET'])
def get_authors():
    """Get all authors"""
    try:
        _, authors_collection, _ = ensure_db()
        authors = list(authors_collection.find({}).sort('au_id', 1))
        return jsonify({
            'success': True, 
            'data': [serialize_author(author) for author in authors]
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/authors', methods=['POST'])
def add_author():
    """Add a new author"""
    try:
        _, authors_collection, _ = ensure_db()
        data = request.json
        au_name = data.get('au_name', '').strip()
        
        if not au_name:
            return jsonify({'success': False, 'error': 'Author last name is required'}), 400
        
        # Create author document
        author = {
            'au_id': generate_author_id(),
            'au_name': au_name,
            'au_fname': data.get('au_fname', '').strip() or None,
            'phone': data.get('phone', '').strip() or None,
            'address': data.get('address', '').strip() or None,
            'city': data.get('city', '').strip() or None,
            'state': data.get('state', '').strip() or None,
            'zip': data.get('zip', '').strip() or None,
            'contract': data.get('contract', False)
        }
        
        # Insert into MongoDB
        result = authors_collection.insert_one(author)
        
        return jsonify({
            'success': True, 
            'message': 'Author added successfully', 
            'id': author['au_id'],
            'mongo_id': str(result.inserted_id)
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500
@app.route('/api/authors/<au_id>', methods=['GET'])
def get_author(au_id):
    """Get a specific author"""
    try:
        author = authors_collection.find_one({'au_id': au_id})
        if author:
            return jsonify({
                'success': True, 
                'data': serialize_author(author)
            })
        else:
            return jsonify({
                'success': False, 
                'error': 'Author not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/authors/<au_id>', methods=['PUT'])
def update_author(au_id):
    """Update an existing author"""
    try:
        data = request.json
        updates = {}
        
        # Only include fields that are provided and not empty
        if 'au_name' in data and data['au_name'].strip():
            updates['au_name'] = data['au_name'].strip()
        if 'au_fname' in data:
            updates['au_fname'] = data['au_fname'].strip() if data['au_fname'].strip() else None
        if 'phone' in data:
            updates['phone'] = data['phone'].strip() if data['phone'].strip() else None
        if 'address' in data:
            updates['address'] = data['address'].strip() if data['address'].strip() else None
        if 'city' in data:
            updates['city'] = data['city'].strip() if data['city'].strip() else None
        if 'state' in data:
            updates['state'] = data['state'].strip() if data['state'].strip() else None
        if 'zip' in data:
            updates['zip'] = data['zip'].strip() if data['zip'].strip() else None
        if 'contract' in data:
            updates['contract'] = bool(data['contract'])
            
        if not updates:
            return jsonify({
                'success': False, 
                'error': 'No valid fields to update'
            }), 400
        
        # Update the author in MongoDB
        result = authors_collection.update_one(
            {'au_id': au_id},
            {'$set': updates}
        )
        
        if result.matched_count == 0:
            return jsonify({
                'success': False, 
                'error': 'Author not found'
            }), 404
            
        return jsonify({
            'success': True, 
            'message': 'Author updated successfully'
        })
            
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/authors/<au_id>', methods=['DELETE'])
def delete_author(au_id):
    """Delete an author and their orphaned books"""
    try:
        # Start a session for transaction
        with client.start_session() as session:
            with session.start_transaction():
                # First, check if author exists
                author = authors_collection.find_one(
                    {'au_id': au_id},
                    session=session
                )
                
                if not author:
                    return jsonify({
                        'success': False, 
                        'error': 'Author not found'
                    }), 404
                
                # Get all titles by this author
                titles = list(titles_collection.find(
                    {'authors.au_id': au_id},
                    {'_id': 1, 'title_id': 1, 'authors': 1},
                    session=session
                ))
                
                # Delete the author
                result = authors_collection.delete_one(
                    {'au_id': au_id},
                    session=session
                )
                
                if result.deleted_count == 0:
                    session.abort_transaction()
                    return jsonify({
                        'success': False, 
                        'error': 'Failed to delete author'
                    }), 500
                
                # Update titles to remove this author and delete any that become orphaned
                for title in titles:
                    # Remove this author from the title's authors array
                    updated_authors = [
                        author for author in title.get('authors', []) 
                        if author.get('au_id') != au_id
                    ]
                    
                    if not updated_authors:
                        # If no authors left, delete the title
                        titles_collection.delete_one(
                            {'_id': title['_id']},
                            session=session
                        )
                    else:
                        # Otherwise, update the authors list
                        titles_collection.update_one(
                            {'_id': title['_id']},
                            {'$set': {'authors': updated_authors}},
                            session=session
                        )
                
                session.commit_transaction()
                return jsonify({
                    'success': True, 
                    'message': 'Author and related data deleted successfully'
                })
                
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

def serialize_title(title):
    """Convert MongoDB document to JSON serializable format"""
    if not title:
        return None
    title['_id'] = str(title['_id'])  # Convert ObjectId to string
    
    # Ensure authors is always a list, even if empty
    if 'authors' not in title:
        title['authors'] = []
    
    # Convert author _id to string if it exists
    for author in title['authors']:
        if '_id' in author:
            author['_id'] = str(author['_id'])
    
    # Convert date to string if it exists
    if 'pubdate' in title and title['pubdate']:
        if isinstance(title['pubdate'], datetime):
            title['pubdate'] = title['pubdate'].strftime('%Y-%m-%d')
    
    return title

# ==================== TITLE ENDPOINTS ====================

@app.route('/api/titles', methods=['GET'])
def get_titles():
    """Get all titles with their authors"""
    try:
        # Use aggregation to get titles with their authors
        pipeline = [
            {
                '$lookup': {
                    'from': 'authors',
                    'localField': 'authors.au_id',
                    'foreignField': 'au_id',
                    'as': 'author_details'
                }
            },
            {
                '$project': {
                    'title_id': 1,
                    'title': 1,
                    'type': 1,
                    'pub_id': 1,
                    'price': 1,
                    'advance': 1,
                    'royalty': 1,
                    'ytd_sales': 1,
                    'notes': 1,
                    'pubdate': 1,
                    'authors': {
                        '$map': {
                            'input': '$authors',
                            'as': 'auth',
                            'in': {
                                'au_id': '$$auth.au_id',
                                'au_ord': '$$auth.au_ord',
                                'royaltyper': '$$auth.royaltyper',
                                'author_details': {
                                    '$arrayElemAt': [
                                        {
                                            '$filter': {
                                                'input': '$author_details',
                                                'as': 'ad',
                                                'cond': {'$eq': ['$$ad.au_id', '$$auth.au_id']}
                                            }
                                        },
                                        0
                                    ]
                                }
                            }
                        }
                    }
                }
            },
            {
                '$project': {
                    'title_id': 1,
                    'title': 1,
                    'type': 1,
                    'pub_id': 1,
                    'price': 1,
                    'advance': 1,
                    'royalty': 1,
                    'ytd_sales': 1,
                    'notes': 1,
                    'pubdate': 1,
                    'authors': {
                        '$map': {
                            'input': '$authors',
                            'as': 'auth',
                            'in': {
                                'au_id': '$$auth.au_id',
                                'au_name': '$$auth.author_details.au_name',
                                'au_fname': '$$auth.author_details.au_fname',
                                'au_ord': '$$auth.au_ord',
                                'royaltyper': '$$auth.royaltyper'
                            }
                        }
                    }
                }
            },
            {'$sort': {'title_id': 1}}
        ]
        
        titles = list(titles_collection.aggregate(pipeline))
        
        return jsonify({
            'success': True, 
            'data': [serialize_title(title) for title in titles]
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/titles', methods=['POST'])
def add_title():
    """Add a new title"""
    try:
        data = request.json
        title = data.get('title', '').strip()
        type_val = data.get('type', '').strip() or None
        pub_id = data.get('pub_id', '').strip() or None
        price = data.get('price')
        advance = data.get('advance')
        royalty = data.get('royalty')
        ytd_sales = data.get('ytd_sales')
        notes = data.get('notes', '').strip() or None
        pubdate = data.get('pubdate')
        authors = data.get('authors', [])  # List of {au_id, royaltyper, au_ord}
        
        if not title or not authors:
            return jsonify({
                'success': False, 
                'error': 'Title and authors are required'
            }), 400
        
        # Convert values - handle None and empty strings
        price_val = float(price) if price is not None and str(price).strip() else None
        advance_val = float(advance) if advance is not None and str(advance).strip() else None
        royalty_val = int(royalty) if royalty is not None and str(royalty).strip() else None
        ytd_sales_val = int(ytd_sales) if ytd_sales is not None and str(ytd_sales).strip() else None
        
        # Process pubdate
        pubdate_obj = None
        if pubdate:
            # Try parsing the date in different formats
            for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y'):
                try:
                    pubdate_obj = datetime.strptime(pubdate, fmt)
                    break
                except ValueError:
                    continue
        
        # Generate unique title ID
        title_id = generate_title_id()
        
        # Prepare authors array with validation
        author_updates = []
        for i, author in enumerate(authors, 1):
            au_id = author.get('au_id')
            if not au_id:
                return jsonify({
                    'success': False, 
                    'error': 'Author ID is required for all authors'
                }), 400
                
            # Verify author exists
            author_doc = authors_collection.find_one({'au_id': au_id})
            if not author_doc:
                return jsonify({
                    'success': False, 
                    'error': f'Author with ID {au_id} not found'
                }), 404
                
            author_updates.append({
                'au_id': au_id,
                'au_ord': author.get('au_ord', i),
                'royaltyper': int(author.get('royaltyper', 100))  # Default to 100%
            })
        
        # Create title document
        title_doc = {
            'title_id': title_id,
            'title': title,
            'type': type_val,
            'pub_id': pub_id,
            'price': price_val,
            'advance': advance_val,
            'royalty': royalty_val,
            'ytd_sales': ytd_sales_val,
            'notes': notes,
            'pubdate': pubdate_obj,
            'authors': author_updates
        }
        
        # Insert into MongoDB
        result = titles_collection.insert_one(title_doc)
        
        return jsonify({
            'success': True, 
            'message': 'Title added successfully', 
            'id': title_id,
            'mongo_id': str(result.inserted_id)
        })
        
    except ValueError as ve:
        return jsonify({
            'success': False, 
            'error': f'Invalid data format: {str(ve)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/titles/<title_id>', methods=['GET'])
def get_title(title_id):
    """Get a specific title with its authors"""
    try:
        # Use aggregation to get the title with author details
        pipeline = [
            {'$match': {'title_id': title_id}},
            {
                '$lookup': {
                    'from': 'authors',
                    'localField': 'authors.au_id',
                    'foreignField': 'au_id',
                    'as': 'author_details'
                }
            },
            {
                '$project': {
                    'title_id': 1,
                    'title': 1,
                    'type': 1,
                    'pub_id': 1,
                    'price': 1,
                    'advance': 1,
                    'royalty': 1,
                    'ytd_sales': 1,
                    'notes': 1,
                    'pubdate': 1,
                    'authors': {
                        '$map': {
                            'input': '$authors',
                            'as': 'auth',
                            'in': {
                                'au_id': '$$auth.au_id',
                                'au_ord': '$$auth.au_ord',
                                'royaltyper': '$$auth.royaltyper',
                                'author_details': {
                                    '$arrayElemAt': [
                                        {
                                            '$filter': {
                                                'input': '$author_details',
                                                'as': 'ad',
                                                'cond': {'$eq': ['$$ad.au_id', '$$auth.au_id']}
                                            }
                                        },
                                        0
                                    ]
                                }
                            }
                        }
                    }
                }
            },
            {
                '$project': {
                    'title_id': 1,
                    'title': 1,
                    'type': 1,
                    'pub_id': 1,
                    'price': 1,
                    'advance': 1,
                    'royalty': 1,
                    'ytd_sales': 1,
                    'notes': 1,
                    'pubdate': 1,
                    'authors': {
                        '$map': {
                            'input': '$authors',
                            'as': 'auth',
                            'in': {
                                'au_id': '$$auth.au_id',
                                'au_name': '$$auth.author_details.au_name',
                                'au_fname': '$$auth.author_details.au_fname',
                                'au_ord': '$$auth.au_ord',
                                'royaltyper': '$$auth.royaltyper'
                            }
                        }
                    }
                }
            }
        ]
        
        title = next(titles_collection.aggregate(pipeline), None)
        
        if not title:
            return jsonify({
                'success': False, 
                'error': 'Title not found'
            }), 404
        
        return jsonify({
            'success': True, 
            'data': serialize_title(title)
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/titles/<title_id>', methods=['PUT'])
def update_title(title_id):
    """Update an existing title"""
    try:
        data = request.json
        
        # Check if title exists
        existing_title = titles_collection.find_one({'title_id': title_id})
        if not existing_title:
            return jsonify({
                'success': False, 
                'error': 'Title not found'
            }), 404
        
        updates = {}
        
        # Only include fields that are provided and not empty
        if 'title' in data and data['title'].strip():
            updates['title'] = data['title'].strip()
        if 'type' in data:
            updates['type'] = data['type'].strip() if data['type'].strip() else None
        if 'pub_id' in data:
            updates['pub_id'] = data['pub_id'].strip() if data['pub_id'].strip() else None
        if 'price' in data and data['price'] is not None:
            price_str = str(data['price']).strip()
            updates['price'] = float(price_str) if price_str else None
        if 'advance' in data and data['advance'] is not None:
            advance_str = str(data['advance']).strip()
            updates['advance'] = float(advance_str) if advance_str else None
        if 'royalty' in data and data['royalty'] is not None:
            royalty_str = str(data['royalty']).strip()
            updates['royalty'] = int(royalty_str) if royalty_str else None
        if 'ytd_sales' in data and data['ytd_sales'] is not None:
            ytd_str = str(data['ytd_sales']).strip()
            updates['ytd_sales'] = int(ytd_str) if ytd_str else None
        if 'notes' in data:
            updates['notes'] = data['notes'].strip() if data['notes'].strip() else None
            
        # Handle pubdate if provided
        if 'pubdate' in data and data['pubdate']:
            pubdate = data['pubdate'].strip()
            # Try parsing the date in different formats
            for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y'):
                try:
                    updates['pubdate'] = datetime.strptime(pubdate, fmt)
                    break
                except ValueError:
                    continue
        
        # Handle authors if provided
        if 'authors' in data and isinstance(data['authors'], list):
            authors = data['authors']
            author_updates = []
            
            for i, author in enumerate(authors, 1):
                au_id = author.get('au_id')
                if not au_id:
                    return jsonify({
                        'success': False, 
                        'error': 'Author ID is required for all authors'
                    }), 400
                
                # Verify author exists
                author_doc = authors_collection.find_one({'au_id': au_id})
                if not author_doc:
                    return jsonify({
                        'success': False, 
                        'error': f'Author with ID {au_id} not found'
                    }), 404
                
                author_updates.append({
                    'au_id': au_id,
                    'au_ord': author.get('au_ord', i),
                    'royaltyper': int(author.get('royaltyper', 100))  # Default to 100%
                })
            
            updates['authors'] = author_updates
        
        # Update the title in MongoDB
        result = titles_collection.update_one(
            {'title_id': title_id},
            {'$set': updates} if updates else {'$setOnInsert': {'title_id': title_id}}
        )
        
        if result.matched_count == 0:
            return jsonify({
                'success': False, 
                'error': 'Failed to update title'
            }), 500
        
        return jsonify({
            'success': True, 
            'message': 'Title updated successfully'
        })
        
    except ValueError as ve:
        return jsonify({
            'success': False, 
            'error': f'Invalid data format: {str(ve)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/titles/<title_id>', methods=['DELETE'])
def delete_title(title_id):
    """Delete a title"""
    try:
        result = titles_collection.delete_one({'title_id': title_id})
        
        if result.deleted_count == 0:
            return jsonify({
                'success': False, 
                'error': 'Title not found'
            }), 404
            
        return jsonify({
            'success': True, 
            'message': 'Title deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/titles/by-author/<au_id>', methods=['GET'])
def get_titles_by_author(au_id):
    """Get all titles by a specific author"""
    try:
        # Find all titles that have this author in their authors array
        pipeline = [
            {'$match': {'authors.au_id': au_id}},
            {
                '$lookup': {
                    'from': 'authors',
                    'localField': 'authors.au_id',
                    'foreignField': 'au_id',
                    'as': 'author_details'
                }
            },
            {
                '$project': {
                    'title_id': 1,
                    'title': 1,
                    'type': 1,
                    'price': 1,
                    'pubdate': 1,
                    'authors': {
                        '$filter': {
                            'input': '$authors',
                            'as': 'auth',
                            'cond': {'$eq': ['$$auth.au_id', au_id]}
                        }
                    },
                    'author_details': {
                        '$arrayElemAt': [
                            {
                                '$filter': {
                                    'input': '$author_details',
                                    'as': 'ad',
                                    'cond': {'$eq': ['$$ad.au_id', au_id]}
                                }
                            },
                            0
                        ]
                    }
                }
            },
            {
                '$project': {
                    'title_id': 1,
                    'title': 1,
                    'type': 1,
                    'price': 1,
                    'pubdate': 1,
                    'royaltyper': {'$arrayElemAt': ['$authors.royaltyper', 0]},
                    'au_name': '$author_details.au_name',
                    'au_fname': '$author_details.au_fname'
                }
            },
            {'$sort': {'title_id': 1}}
        ]
        
        titles = list(titles_collection.aggregate(pipeline))
        
        # Convert ObjectIds and dates to JSON serializable format
        serialized_titles = []
        for title in titles:
            # Serialize all ObjectIds recursively
            title = serialize_objectid(title)
            # Convert dates to display string (DD-MM-YYYY)
            if 'pubdate' in title and title['pubdate'] and isinstance(title['pubdate'], datetime):
                title['pubdate'] = title['pubdate'].strftime('%d-%m-%Y')
            serialized_titles.append(title)
        
        return jsonify({
            'success': True, 
            'data': serialized_titles
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if the API and database are working"""
    try:
        # Ensure MongoDB is initialized
        ensure_db()
        # Try to ping the database
        client.admin.command('ping')
        return jsonify({
            'success': True, 
            'message': 'API and database are healthy'
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Production: use environment variable for port, debug=False
    # Development: debug=True
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    # For Render, must bind to 0.0.0.0 and use PORT env var
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
