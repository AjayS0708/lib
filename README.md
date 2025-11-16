# 📚 Author & Title Manager

A modern, responsive web application for managing authors and book titles with MongoDB. Built with Flask backend and vanilla JavaScript frontend.

## ✨ Features

### Author Management
- Complete author profiles with auto-generated IDs (XXX-XX-XXXX format)
- Full contact information (name, phone, address, city, state, ZIP)
- Contract status tracking
- Add, edit, and delete authors
- View all authors in an organized list

### Title Management
- Comprehensive title information with auto-generated IDs (LLNNNN format)
- Book details (title, genre, publisher ID, price, advance, royalty, sales)
- Publication dates and notes
- Link titles to multiple authors with individual royalty percentages
- Add, edit, and delete titles
- View all titles with author information

### Advanced Features
- Multiple authors per title with order tracking
- Individual royalty percentages per author
- View all titles by a specific author
- Automatic cleanup of orphaned titles when deleting authors
- Real-time updates and notifications
- Responsive design for all devices

## 🗄️ Database

The application uses **MongoDB** with two collections:

### authors
- `au_id` - Author ID (format: XXX-XX-XXXX)
- `au_name` - Last name (required)
- `au_fname` - First name
- `phone` - Phone number
- `address` - Street address
- `city` - City
- `state` - State
- `zip` - ZIP code
- `contract` - Contract status (boolean)

### titles
- `title_id` - Title ID (format: LLNNNN)
- `title` - Title name (required)
- `type` - Genre/type
- `pub_id` - Publisher ID
- `price` - Price
- `advance` - Advance payment
- `royalty` - Royalty percentage
- `ytd_sales` - Year-to-date sales
- `notes` - Additional notes
- `pubdate` - Publication date
- `authors` - Array of authors with:
  - `au_id` - Author ID
  - `au_ord` - Author order
  - `royaltyper` - Author's royalty percentage

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or cloud instance like MongoDB Atlas)
- pip (Python package manager)

### Installation

1. **Clone or download the project**
   ```bash
   cd BooksDB
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Create a `.env` file in the project root:
   ```env
   MONGODB_URI=mongodb://localhost:27017/
   DB_NAME=BooksDB
   FLASK_DEBUG=False
   PORT=5000
   ```

   For MongoDB Atlas:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
   DB_NAME=BooksDB
   ```

4. **Run the application**

   **Option A: Using the start script (Windows)**
   ```bash
   start.bat
   ```

   **Option B: Run directly**
   ```bash
   python app.py
   ```

5. **Open in browser**
   
   Navigate to: `http://localhost:5000`

## 📁 Project Structure

```
BooksDB/
├── app.py                  # Flask backend with API endpoints
├── requirements.txt        # Python dependencies
├── start.bat              # Quick start script (Windows)
├── .env                   # Environment variables (create this)
├── .gitignore             # Git ignore rules
├── templates/
│   └── index.html         # Main HTML template
└── static/
    ├── style.css          # Styling and responsive design
    └── script.js          # Frontend JavaScript logic
```

## 🎨 Technology Stack

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing
- **PyMongo** - MongoDB driver for Python
- **Python-dotenv** - Environment variable management

### Frontend
- **HTML5** - Structure
- **CSS3** - Modern styling with responsive design
- **Vanilla JavaScript** - Pure JS for maximum performance
- **Font Awesome** - Icons

## 🔌 API Endpoints

### Authors
- `GET /api/authors` - Get all authors
- `POST /api/authors` - Add a new author
- `GET /api/authors/<au_id>` - Get a specific author
- `PUT /api/authors/<au_id>` - Update an author
- `DELETE /api/authors/<au_id>` - Delete an author (and orphaned titles)

### Titles
- `GET /api/titles` - Get all titles with authors
- `POST /api/titles` - Add a new title
- `GET /api/titles/<title_id>` - Get a specific title
- `PUT /api/titles/<title_id>` - Update a title
- `DELETE /api/titles/<title_id>` - Delete a title
- `GET /api/titles/by-author/<au_id>` - Get all titles by an author

### Health
- `GET /api/health` - Check API and database status

## 🎯 Usage Guide

### Managing Authors
1. Go to the **Authors** tab
2. Fill in the author details (Last name is required)
3. Click **Add Author** (ID is auto-generated)
4. To edit: Click on an author in the list, modify details, click **Update**
5. To delete: Select an author and click **Delete**

### Managing Titles
1. Go to the **Titles** tab
2. In the "Add New Title" section, enter:
   - Title name (required)
   - Select an author (required)
   - Fill in other details as needed
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

## 🌐 Deployment

### Environment Variables for Production

Set these environment variables on your hosting platform:

```env
MONGODB_URI=your_mongodb_connection_string
DB_NAME=BooksDB
FLASK_DEBUG=False
PORT=5000
```

### Deployment Platforms

#### Heroku
1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: gunicorn app:app
   ```
3. Deploy:
   ```bash
   heroku create
   git push heroku main
   heroku config:set MONGODB_URI=your_mongodb_uri
   ```

#### PythonAnywhere
1. Upload files via Files tab
2. Set up web app with Flask
3. Configure environment variables in web app settings
4. Use MongoDB Atlas (cloud) or set up local MongoDB

#### Railway
1. Connect GitHub repository
2. Add MongoDB service or use external MongoDB Atlas
3. Set environment variables
4. Deploy automatically

#### Render
1. Connect GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn app:app`
4. Add MongoDB Atlas connection string to environment variables

### Production Checklist

- [ ] Set `FLASK_DEBUG=False` in production
- [ ] Use MongoDB Atlas or secure MongoDB instance
- [ ] Set strong MongoDB credentials
- [ ] Enable HTTPS/SSL
- [ ] Use environment variables for all sensitive data
- [ ] Set up MongoDB backups
- [ ] Test all CRUD operations
- [ ] Configure error logging
- [ ] Set up monitoring

## 🐛 Troubleshooting

### Database Connection Error
- Check MongoDB is running (if local) or connection string is correct
- Verify MongoDB Atlas network access settings
- Check credentials in `.env` file

### Port Already in Use
- Change port in environment variables: `PORT=5001`
- Or stop the process using port 5000

### Module Not Found Error
- Run `pip install -r requirements.txt`
- Make sure virtual environment is activated

### MongoDB Connection Issues
- For MongoDB Atlas: Check IP whitelist and credentials
- For local MongoDB: Ensure MongoDB service is running
- Verify connection string format

## 🔒 Security Notes

⚠️ **Important for production:**

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use strong MongoDB credentials**
3. **Enable HTTPS/SSL** on hosting platform
4. **Use MongoDB Atlas** with network access restrictions
5. **Validate all inputs** on server side (already implemented)
6. **Consider adding authentication** for public deployments

## 📝 License

This project is open source and available for personal and educational use.

## 🤝 Contributing

Feel free to fork, modify, and improve this application!

---

**Enjoy managing your library! 📚✨**
