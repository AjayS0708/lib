# 📚 Author & Title Manager

A complete web-based library management system with professional database schema.

## 🎯 Project Overview

This application manages authors and book titles with a comprehensive database structure including:
- Full author contact information
- Detailed title information (pricing, royalties, sales)
- Many-to-many relationships with royalty tracking
- Modern, responsive web interface

## 📊 Database Schema

```
authors                    titleauthor              titles
├─ au_id (PK)         ┌──→ au_id (FK)             ├─ title_id (PK)
├─ au_name            │    title_id (FK) ←────────┤  title
├─ au_fname           │    au_ord                 │  type
├─ phone              │    royaltyper             │  pub_id
├─ address            └──                         │  price
├─ city                                           │  advance
├─ state                                          │  royalty
├─ zip                                            │  ytd_sales
└─ contract                                       │  notes
                                                  └─ pubdate
```

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup database:**
   ```bash
   python setup_database.py
   ```

3. **Run application:**
   ```bash
   python web_app.py
   ```

4. **Open browser:**
   ```
   http://localhost:5000
   ```

## 📁 File Structure

```
Author-Title-Manager/
├── web_app.py              # Flask backend (15KB)
├── schema.sql              # Database schema with sample data
├── setup_database.py       # Automated database setup
├── requirements.txt        # Python dependencies
├── start.bat               # Windows quick start script
├── templates/
│   └── index.html          # Frontend HTML
├── static/
│   ├── style.css           # Responsive CSS styling
│   └── script.js           # JavaScript functionality
├── README.md               # Complete documentation
├── QUICK_START.txt         # Quick reference guide
└── .env.example            # Environment variables template
```

## 🛠️ Technology Stack

- **Backend:** Flask (Python)
- **Database:** MySQL
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Icons:** Font Awesome

## ✨ Key Features

### Authors Management
- Auto-generated IDs (XXX-XX-XXXX format)
- Full contact information
- Contract status tracking
- CRUD operations

### Titles Management
- Auto-generated IDs (LLNNNN format)
- Comprehensive book details
- Financial tracking (price, advance, royalty)
- Sales tracking
- Publication dates
- CRUD operations

### Relationships
- Multiple authors per title
- Author ordering
- Individual royalty percentages
- Automatic orphan cleanup

### User Interface
- Modern, responsive design
- Tab-based navigation
- Real-time notifications
- Form validation
- Mobile-friendly

## 📦 Sample Data Included

- 5 Authors (White, Green, Carson, O'Leary, Straight)
- 5 Titles (Business and Cooking books)
- Author-title relationships with royalty splits

## 🔒 Security Notes

**Before deploying to production:**
1. Change database password
2. Use environment variables
3. Enable HTTPS
4. Add authentication
5. Validate all inputs

## 📖 Documentation

- **README.md** - Complete documentation with API endpoints
- **QUICK_START.txt** - Quick reference guide
- **schema.sql** - Database structure with comments

## 🌐 Deployment Ready

This application can be deployed to:
- PythonAnywhere (Free tier)
- Heroku
- Railway
- DigitalOcean
- Any platform supporting Flask + MySQL

## 📝 License

Open source - Free for personal and educational use

## 🤝 Support

For issues or questions, refer to README.md or QUICK_START.txt

---

**Built with ❤️ for efficient library management**
