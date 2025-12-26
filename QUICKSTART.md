# 🚀 Quick Start Guide - School Management System

## Step-by-Step Setup (5 Minutes)

### 1. Prerequisites Check

Ensure you have:
- Python 3.10 or higher installed
- pip package manager
- Command prompt/terminal access

Check Python version:
```bash
python --version
```

### 2. Set Up Virtual Environment

Open your terminal in the project directory and run:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install Django and all required packages. It may take 2-3 minutes.

### 4. Configure Environment

Create `.env` file from the example:

```bash
# Windows PowerShell:
Copy-Item .env.example .env

# Windows Command Prompt:
copy .env.example .env

# Linux/Mac:
cp .env.example .env
```

**For quick start, the default `.env` settings will work fine!**

### 5. Set Up Database

Run these commands to create the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

You should see output showing successful migrations.

### 6. Create Admin Account

```bash
python manage.py createsuperuser
```

When prompted, enter:
- Username: `admin` (or your choice)
- Email: your email
- Password: strong password (minimum 8 characters)
- Confirm password

### 7. Start the Server

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

### 8. Access the Application

Open your browser and visit:
- **Main Application:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/

Login with the superuser credentials you created.

---

## 🎯 First Steps After Login

### As Admin:

1. **Add Academic Year**
   - Go to Admin Panel → Academic Years
   - Click "Add Academic Year"
   - Set dates and mark as current

2. **Create Classes**
   - Admin Panel → Class Rooms
   - Add classes (e.g., Grade 1, Grade 2)

3. **Add Subjects**
   - Admin Panel → Subjects
   - Create subjects (Math, English, Science, etc.)

4. **Create Teacher Account**
   - Admin Panel → Users
   - Add new user with role "Teacher"
   - Then create Teacher profile linking to that user

5. **Add Students**
   - Admin Panel → Students
   - Create student profiles

6. **Set Fee Structure**
   - Admin Panel → Fee Structures
   - Define fees for each class

---

## 🧪 Testing the System

### Test Data Creation

You can quickly create test data through the admin panel:

1. **Create a Test Student:**
   - First create a User with role "Student"
   - Then create Student profile
   - Assign to a class

2. **Test Attendance:**
   - Go to Attendance section
   - Mark attendance for a class

3. **Test Fees:**
   - Record a payment for a student
   - View fee balance

4. **Test Exams:**
   - Create an exam
   - Add exam schedule
   - Enter results

---

## 📱 User Access by Role

### Admin Dashboard
- URL: http://127.0.0.1:8000/dashboard/
- Full access to all modules

### Teacher Portal
- Mark attendance
- Enter grades
- View class information

### Student Portal
- View attendance
- Check grades
- See fee status

### Parent Portal
- View children's records
- Check attendance and results
- View fee payments

---

## 🔧 Common Commands

```bash
# Start server
python manage.py runserver

# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test

# Check for issues
python manage.py check

# Open Django shell
python manage.py shell
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use different port
python manage.py runserver 8080
```

### Migration Issues
```bash
# Reset database (CAUTION: Deletes all data!)
python manage.py flush
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

### Module Not Found Error
```bash
# Reinstall requirements
pip install -r requirements.txt --upgrade
```

---

## 🎨 Customization

### Change Site Name
Edit `config/settings.py`:
```python
# Line ~200
admin.site.site_header = "Your School Name"
admin.site.site_title = "Your School Admin"
```

### Change Colors
Edit `static/css/style.css`:
```css
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
}
```

### Add Logo
Place your logo in `static/images/logo.png` and update templates.

---

## 📚 Next Steps

1. **Explore Admin Panel** - Get familiar with all sections
2. **Create Sample Data** - Add test students, teachers, classes
3. **Test Features** - Try attendance, fees, exams
4. **Read Full Documentation** - Check README.md for details
5. **Customize** - Adapt to your school's needs

---

## 🆘 Getting Help

- **Documentation:** See README.md
- **Common Issues:** Check TROUBLESHOOTING.md
- **Django Docs:** https://docs.djangoproject.com/
- **Bootstrap Docs:** https://getbootstrap.com/docs/

---

## 💡 Tips

- Always keep your virtual environment activated when working
- Make database backups regularly
- Test on development before production
- Use strong passwords for all accounts
- Keep your SECRET_KEY secret in production

---

**Happy Managing! 🎓**
