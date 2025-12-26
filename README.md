# School Management System (SMS / ERP)

A comprehensive, professional School Management System built with Django, HTML, CSS, and JavaScript. This system provides complete management capabilities for educational institutions including student management, teacher management, attendance tracking, fee management, exam management, and more.

## 🚀 Features

### Core Modules

- **User Management & Authentication**
  - Role-based access control (Admin, Teacher, Student, Parent, Staff)
  - Custom user model with profile management
  - Secure authentication and authorization

- **Student Management**
  - Student enrollment and profile management
  - Admission number generation
  - Class assignment and tracking
  - Medical records and documents

- **Teacher Management**
  - Teacher profiles with qualifications
  - Subject assignments
  - Class teacher designation

- **Parent Management**
  - Parent/Guardian profiles
  - Multiple children linking
  - Emergency contact information

- **Class & Subject Management**
  - Class and stream organization
  - Subject allocation
  - Timetable management
  - Academic year tracking

- **Attendance Management**
  - Daily attendance marking
  - Attendance reports and analytics
  - Monthly attendance summaries

- **Fees Management**
  - Fee structure configuration
  - Payment recording and tracking
  - Receipt generation
  - Fee balance tracking

- **Exam Management**
  - Exam scheduling
  - Multiple exam types support
  - Exam timetable generation

- **Results Management**
  - Marks entry and grading
  - Report card generation
  - Performance analytics
  - Grade calculation

- **Promotion Management**
  - Class promotion workflow
  - Student graduation tracking

- **Notifications & Notice Board**
  - School-wide announcements
  - Targeted notifications
  - Internal messaging system

## 🛠️ Technology Stack

- **Backend:** Django 4.2+ / Python 3.10+
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Database:** SQLite (development) / PostgreSQL (production)
- **API:** Django REST Framework
- **PDF Generation:** ReportLab, WeasyPrint
- **Authentication:** Django Auth with custom User model

## 📋 Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- PostgreSQL (for production) or SQLite (for development)

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
cd "School management(SMS)"
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy `.env.example` to `.env` and configure your settings:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# For PostgreSQL (Production)
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=school_db
# DB_USER=school_user
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. Load Initial Data (Optional)

```bash
# Create some sample data if needed
python manage.py loaddata fixtures/initial_data.json
```

### 8. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 9. Run Development Server

```bash
python manage.py runserver
```

Access the application at: `http://127.0.0.1:8000/`

## 👥 Default User Roles

After creating a superuser, you can create users for different roles:

1. **Admin** - Full system access
2. **Teacher** - Manage classes, attendance, grades
3. **Student** - View grades, attendance, fees
4. **Parent** - View children's information
5. **Staff** - Limited access based on department

## 📁 Project Structure

```
School management(SMS)/
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── api_urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── accounts/          # User authentication & management
│   ├── students/          # Student management
│   ├── teachers/          # Teacher management
│   ├── parents/           # Parent management
│   ├── staff/             # Staff management
│   ├── classes/           # Class & subject management
│   ├── attendance/        # Attendance tracking
│   ├── fees/              # Fee management
│   ├── exams/             # Exam management
│   ├── results/           # Results & grades
│   ├── promotions/        # Student promotions
│   └── notifications/     # Notifications & notices
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── partials/
│   └── auth/
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
│
└── media/                 # User uploaded files
```

## 🔐 Security Features

- CSRF protection
- Password hashing
- Role-based access control
- Secure session management
- SQL injection prevention
- XSS protection
- Audit logging

## 📊 Admin Panel

Access the Django admin panel at: `http://127.0.0.1:8000/admin/`

Features:
- User management
- Complete CRUD operations for all models
- Data import/export
- Advanced filtering and search
- Inline editing

## 🎨 Customization

### Adding New Modules

1. Create a new Django app:
```bash
python manage.py startapp module_name
```

2. Add to `INSTALLED_APPS` in `config/settings.py`
3. Create models, views, and templates
4. Register URLs in `config/urls.py`

### Custom Themes

Edit `static/css/style.css` to customize colors, fonts, and layouts.

## 📝 API Documentation

The system includes RESTful APIs for integration:

- `/api/students/` - Student operations
- `/api/teachers/` - Teacher operations
- `/api/attendance/` - Attendance operations
- `/api/results/` - Results operations

API authentication uses Token-based authentication.

## 🧪 Testing

Run tests:

```bash
python manage.py test
```

## 📦 Production Deployment

### Using Gunicorn + Nginx

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Create Gunicorn config:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

3. Configure Nginx as reverse proxy

4. Set up SSL certificate

5. Configure environment variables for production

### Using Docker (Recommended)

```bash
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Support

For support, email support@schoolsystem.com or create an issue in the repository.

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] SMS notifications
- [ ] Email integration
- [ ] Parent portal
- [ ] Online exam system
- [ ] Library management
- [ ] Transport management
- [ ] Hostel management
- [ ] Inventory management
- [ ] HR & Payroll

## 📸 Screenshots

(Add screenshots of your application here)

## ⚙️ Advanced Configuration

### Email Configuration (Gmail)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Backup

```bash
# Backup
python manage.py dumpdata > backup.json

# Restore
python manage.py loaddata backup.json
```

### Performance Optimization

- Enable caching (Redis)
- Use CDN for static files
- Database query optimization
- Enable compression

## 🐛 Troubleshooting

### Common Issues

**Issue:** Migration errors
```bash
python manage.py migrate --run-syncdb
```

**Issue:** Static files not loading
```bash
python manage.py collectstatic --clear
```

**Issue:** Permission denied
```bash
python manage.py check --deploy
```

## 📞 Contact

- **Project Maintainer:** Your Name
- **Email:** your.email@example.com
- **Website:** https://yourwebsite.com

---

**Built with ❤️ for Educational Institutions**
