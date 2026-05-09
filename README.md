# InterviewGuard

InterviewGuard is a lightweight interview preparation and interview protection platform designed for students, graduates, and job seekers.

The platform helps users:

* Prepare for interviews using curated interview questions
* Build stronger attachment-ready CVs
* Test internet connection quality before online interviews
* Monitor network stability during interviews
* Automatically prepare fail-safe communication when connectivity issues occur

Built with a focus on accessibility and real-world connectivity conditions in Zimbabwe.

---

# Features

## 🚀 Network Readiness Test

* Real-time download speed testing
* Upload speed analysis
* Ping / latency measurement
* Interview success probability estimation
* Platform-specific readiness insights (Zoom, Teams, Meet, etc.)

---

## 🛡 Interview Guard

* Background network monitoring
* Detects unstable internet connections
* Browser notifications
* Interview countdown reminders
* Automatic apology email preparation during severe connection drops

---

## 📚 Interview Preparation

* Faculty-based interview questions
* Beginner to advanced difficulty levels
* Search and filtering support
* Community-driven question submissions
* Support for:

  * Computer Science
  * Engineering
  * Business
  * Medicine
  * Law
  * Education
  * Arts
  * Social Sciences
  * Natural Sciences

---

## 📄 CV Support

Guides students on creating professional attachment-ready CVs by covering:

* Personal details
* Education
* Technical skills
* Projects
* References
* Professional summaries

---

# Tech Stack

## Frontend

* HTML5
* CSS3
* Vanilla JavaScript

## Backend

* Django
* Django REST Framework

## Database

* MySQL

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/chikumbu-kudakwashe/interviewguard.git
cd interviewguard
```

---

## 2. Create a virtual environment

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# MySQL Database Setup

Create a MySQL database:

```sql
CREATE DATABASE interviewguard;
```

Update your Django `settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "interviewguard",
        "USER": "root",
        "PASSWORD": "your_password",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    }
}
```

---

# Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

# Create Superuser

```bash
python manage.py createsuperuser
```

---

# Start Development Server

```bash
python manage.py runserver
```

Backend will run on:

```txt
http://127.0.0.1:8000/
```

---

# API Features

The backend supports:

* Interview question management
* Question submissions
* CV builder recommendations
* Admin approval workflows
* Search and filtering
* REST APIs for frontend integration

---

# Project Goals

InterviewGuard aims to:

* Reduce interview anxiety
* Improve interview preparation accessibility
* Help students succeed in online interviews
* Support attachment and internship readiness
* Provide lightweight tools optimized for low-bandwidth environments

---

# Developer

Developed by Kudakwashe Chikumbu.
```link
vachikumbu.com
```

For technical support:

```txt
kudakwashe@vachikumbu.com
```

General platform enquiries:

```txt
interviewguard@vachikumbu.com
```

---

# Version

```txt
v1.0.0
```

---

# License

This project is intended for educational and portfolio purposes.
