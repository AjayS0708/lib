# 🚀 Deployment Checklist

Use this checklist before deploying your application to production.

## ✅ Pre-Deployment Checklist

### Security
- [ ] Change database password from default
- [ ] Move credentials to environment variables (.env file)
- [ ] Update `web_app.py` to use `os.getenv()` for all sensitive data
- [ ] Add `.env` to `.gitignore` (already done)
- [ ] Enable HTTPS/SSL on hosting platform
- [ ] Add authentication/login system (if needed)
- [ ] Implement rate limiting
- [ ] Add CSRF protection
- [ ] Sanitize all user inputs

### Database
- [ ] Backup existing data
- [ ] Test database connection on hosting platform
- [ ] Update database host/credentials for production
- [ ] Run `schema.sql` on production database
- [ ] Verify all tables created successfully
- [ ] Test sample data insertion
- [ ] Set up automated backups

### Application
- [ ] Test all CRUD operations locally
- [ ] Test with multiple users/sessions
- [ ] Check error handling
- [ ] Verify all API endpoints work
- [ ] Test on different browsers
- [ ] Test on mobile devices
- [ ] Remove debug mode (`debug=False` in web_app.py)
- [ ] Set proper host and port for production

### Code Quality
- [ ] Remove console.log statements from JavaScript
- [ ] Remove commented-out code
- [ ] Check for TODO/FIXME comments
- [ ] Verify no hardcoded passwords in code
- [ ] Test error messages don't expose sensitive info

### Documentation
- [ ] Update README with production URL
- [ ] Document environment variables needed
- [ ] Add API documentation (if public)
- [ ] Create user guide/manual
- [ ] Document backup/restore procedures

## 🌐 Platform-Specific Setup

### PythonAnywhere
- [ ] Create account at pythonanywhere.com
- [ ] Upload all files
- [ ] Set up MySQL database
- [ ] Configure web app with Flask
- [ ] Set environment variables in web app settings
- [ ] Update allowed hosts
- [ ] Test application

### Heroku
- [ ] Install Heroku CLI
- [ ] Create `Procfile`: `web: python web_app.py`
- [ ] Create `runtime.txt` with Python version
- [ ] Add ClearDB MySQL addon
- [ ] Set config vars (environment variables)
- [ ] Deploy: `git push heroku main`
- [ ] Run database setup
- [ ] Test application

### Railway
- [ ] Create account at railway.app
- [ ] Connect GitHub repository
- [ ] Add MySQL database service
- [ ] Set environment variables
- [ ] Configure start command
- [ ] Deploy automatically
- [ ] Test application

### DigitalOcean
- [ ] Create droplet or use App Platform
- [ ] Install Python and MySQL
- [ ] Clone repository
- [ ] Set up virtual environment
- [ ] Install dependencies
- [ ] Configure MySQL
- [ ] Set up systemd service or use App Platform
- [ ] Configure domain/SSL
- [ ] Test application

## 🔧 Configuration Changes for Production

### web_app.py
```python
# Change this:
app.run(debug=True, host='0.0.0.0', port=5000)

# To this:
app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
```

### Database Configuration
```python
# Use environment variables:
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'),  # No default!
    'database': os.getenv('DB_NAME', 'BooksDB')
}
```

## 📊 Post-Deployment Verification

- [ ] Application loads without errors
- [ ] Can view authors list
- [ ] Can add new author
- [ ] Can edit author
- [ ] Can delete author
- [ ] Can view titles list
- [ ] Can add new title
- [ ] Can edit title with multiple authors
- [ ] Can delete title
- [ ] Can view titles by author
- [ ] All forms validate correctly
- [ ] Error messages display properly
- [ ] Toast notifications work
- [ ] Responsive design works on mobile
- [ ] Database persists data correctly

## 🔍 Monitoring

After deployment, monitor:
- [ ] Application uptime
- [ ] Response times
- [ ] Error logs
- [ ] Database performance
- [ ] Storage usage
- [ ] User activity (if applicable)

## 🆘 Rollback Plan

If something goes wrong:
1. [ ] Keep backup of previous version
2. [ ] Document rollback procedure
3. [ ] Have database backup ready
4. [ ] Test rollback in staging first
5. [ ] Notify users if needed

## 📝 Maintenance Schedule

- [ ] Weekly: Check error logs
- [ ] Monthly: Review database performance
- [ ] Monthly: Update dependencies
- [ ] Quarterly: Security audit
- [ ] Yearly: Review and update documentation

---

**Remember:** Always test in a staging environment before deploying to production!
