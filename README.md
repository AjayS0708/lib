# 📚 Author & Title Manager - Updated Web Application

A modern, responsive web application for managing authors and book titles with comprehensive fields matching a professional publishing database schema. Built with Flask (Python) backend and vanilla JavaScript frontend.

## ✨ Features

### Author Management
- **Complete Author Profiles**
  - Author ID (auto-generated: XXX-XX-XXXX format)
  - Last Name and First Name
  - Phone number
  - Full address (street, city, state, ZIP)
  - Contract status
- Add, edit, and delete authors
- View all authors in an organized list

### Title Management
- **Comprehensive Title Information**
  - Title ID (auto-generated: LLNNNN format)
  - Title name
  - Type/Genre (business, cooking, computing, psychology, etc.)
  - Publisher ID
  - Price, Advance, and Royalty percentage
  - Year-to-date sales
  - Publication date
  - Notes
- Link titles to multiple authors with individual royalty percentages
- Add, edit, and delete titles
- View all titles with author information

### Advanced Features
- **Author-Title Relationships**
  - Multiple authors per title
  - Author order tracking
  - Individual royalty percentages per author
- View all titles by a specific author
- Automatic cleanup of orphaned titles when deleting authors
- Real-time updates and notifications
- Responsive design for all devices

## 🗄️ Database Schema

The application uses three main tables:

### authors
- `au_id` (VARCHAR(11), PRIMARY KEY) - Format: XXX-XX-XXXX
- `au_name` (VARCHAR(100)) - Last name
- `au_fname` (VARCHAR(50)) - First name
- `phone` (VARCHAR(20))
- `address` (VARCHAR(100))
- `city` (VARCHAR(50))
- `state` (VARCHAR(2))
- `zip` (VARCHAR(10))
- `contract` (BOOLEAN)

### titles
- `title_id` (VARCHAR(6), PRIMARY KEY) - Format: LLNNNN
- `title` (VARCHAR(255))
- `type` (VARCHAR(50))
- `pub_id` (VARCHAR(4))
- `price` (DECIMAL(10,2))
- `advance` (DECIMAL(10,2))
- `royalty` (INT) - Overall royalty percentage
- `ytd_sales` (INT) - Year-to-date sales
- `notes` (TEXT)
- `pubdate` (DATE)

### titleauthor (Junction Table)
- `au_id` (VARCHAR(11), FOREIGN KEY)
- `title_id` (VARCHAR(6), FOREIGN KEY)
- `au_ord` (INT) - Author order
- `royaltyper` (INT) - Individual author's royalty percentage

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

### Installation

1. **Navigate to the project directory**
   ```bash
   cd "C:\Users\ajays\OneDrive\Desktop\Amazon Clone"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**

   **Option A: Using Python script (Recommended)**
   ```bash
   python setup_database.py
   ```

   **Option B: Using MySQL directly**
   ```bash
   mysql -u root -p BooksDB < schema.sql
   ```

   **Option C: Manual setup**
   - Open MySQL Workbench or command line
   - Connect to your MySQL server
   - Run the contents of `schema.sql`

4. **Run the application**
   ```bash
   python web_app.py
   ```
   
   Or use the quick start script:
   ```bash
   start.bat
   ```

5. **Open in browser**
   
   Navigate to: `http://localhost:5000`

## 📁 Project Structure

```
Amazon Clone/
├── web_app.py              # Flask backend with API endpoints
├── schema.sql              # Database schema with sample data
├── setup_database.py       # Python script to set up database
├── setup_database.bat      # Windows batch script for database setup
├── start.bat               # Quick start script
├── templates/
│   └── index.html          # Main HTML template
├── static/
│   ├── style.css           # Styling and responsive design
│   └── script.js           # Frontend JavaScript logic
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── UPDATED_README.md      # This file
```

## 🎨 Technology Stack

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing
- **MySQL Connector** - Database connectivity
- **Python-dotenv** - Environment variable management

### Frontend
- **HTML5** - Structure
- **CSS3** - Modern styling with gradients, animations, and responsive design
- **Vanilla JavaScript** - No frameworks, pure JS for maximum performance
- **Font Awesome** - Beautiful icons

## 🔌 API Endpoints

### Authors
- `GET /api/authors` - Get all authors
- `POST /api/authors` - Add a new author
- `GET /api/authors/<au_id>` - Get a specific author
- `PUT /api/authors/<au_id>` - Update an author
- `DELETE /api/authors/<au_id>` - Delete an author

### Titles
- `GET /api/titles` - Get all titles
- `POST /api/titles` - Add a new title
- `GET /api/titles/<title_id>` - Get a specific title
- `PUT /api/titles/<title_id>` - Update a title
- `DELETE /api/titles/<title_id>` - Delete a title
- `GET /api/titles/by-author/<au_id>` - Get titles by author

### Health
- `GET /api/health` - Check API and database status

## 🎯 Usage Guide

### Managing Authors
1. Go to the **Authors** tab
2. Fill in the author details:
   - Last name (required)
   - First name, phone, address, city, state, ZIP (optional)
   - Check "Has Contract" if applicable
3. Click **Add Author** (ID is auto-generated)
4. To edit: Click on an author in the list, modify details, click **Update**
5. To delete: Select an author and click **Delete**

### Managing Titles
1. Go to the **Titles** tab
2. In the "Add New Title" section, enter:
   - Title name (required)
   - Type, publisher ID, price, advance, royalty, sales
   - Select an author (required)
   - Set author's royalty percentage
   - Publication date and notes
3. Click **Add Title** (ID is auto-generated)
4. To edit: Click on a title in the list
   - Modify details
   - Select multiple authors with individual royalty percentages
   - Click **Update Title**
5. To delete: Select a title and click **Delete Title**

### View Titles by Author
1. Go to the **View by Author** tab
2. Select an author from the dropdown
3. Click **Show Titles**
4. View all titles by that author with royalty information

## 📊 Sample Data

The `schema.sql` file includes sample data:
- 5 sample authors (White, Green, Carson, O'Leary, Straight)
- 5 sample titles (business and cooking books)
- Author-title relationships with royalty splits

## 🐛 Troubleshooting

### Database Connection Error
- Ensure MySQL server is running
- Check database credentials in `web_app.py` (line 15)
- Verify `BooksDB` database exists
- Run `setup_database.py` to create tables

### Port Already in Use
- Change the port in `web_app.py` (last line):
  ```python
  app.run(debug=True, host='0.0.0.0', port=5001)
  ```

### Module Not Found Error
- Run `pip install -r requirements.txt`

### Schema Errors
- Drop existing tables manually if needed:
  ```sql
  DROP TABLE IF EXISTS titleauthor;
  DROP TABLE IF EXISTS titles;
  DROP TABLE IF EXISTS authors;
  ```
- Then run `setup_database.py` again

## 🔄 Migrating from Old Schema

If you have data in the old schema (AuthorID, AuthorName, TitleID, BookTitle):

1. **Backup your data first!**
2. Export existing data
3. Run the new schema setup
4. Manually import data with field mapping:
   - `AuthorID` → `au_id` (may need reformatting)
   - `AuthorName` → `au_name`
   - `TitleID` → `title_id` (may need reformatting)
   - `BookTitle` → `title`

## 🌐 Hosting Options

Same as before:
- PythonAnywhere (Free tier available)
- Heroku
- Railway
- DigitalOcean App Platform

See `WEB_README.md` for detailed hosting instructions.

## 🔒 Security Notes

⚠️ **Important for production:**

1. **Use environment variables** for database credentials
2. **Never commit passwords** to Git
3. **Use HTTPS** in production
4. **Add authentication** if hosting publicly
5. **Validate all inputs** on the server side

## 📝 License

This project is open source and available for personal and educational use.

## 🤝 Contributing

Feel free to fork, modify, and improve this application!

---

**Enjoy managing your publishing database! 📚✨**
