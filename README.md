# 🌍 Community Waste Management System

A full-stack Django web application that enables citizens to report waste with live location, allowing municipality officers to manage reports efficiently and assign them to workers for resolution.
Live: https://community-waste-management-system.onrender.com

---

## 📌 Project Overview

The **Community Waste Management System** is designed to bridge the gap between the public and local municipalities by providing a centralized platform for reporting and managing waste complaints.

Citizens can submit waste reports with images and GPS locations. Municipality officers receive reports belonging only to their municipality, assign them to workers, and monitor the entire resolution process until completion.

---

## 🚀 Features

### 👤 Public Users

- User Registration & Login
- Report waste with:
  - Image upload
  - Description
  - GPS Location
  - Landmark
- View personal complaint history
- Track complaint status
- Receive status update notifications

---

### 🏛 Municipality Officers

- Municipality Registration
- Admin Approval System
- Municipality Dashboard
- View reports assigned to their municipality
- Assign reports to workers
- Update report status
- View analytics and notifications

---

### 👷 Workers

- Secure Worker Login
- Worker Dashboard
- View assigned tasks
- Update work status
- Upload completion image
- Add work notes

---

### 👑 Admin

- Manage Users
- Approve Municipality Requests
- Monitor Reports
- Manage Workers
- System Overview Dashboard

---

## 🛠 Tech Stack

### Backend

- Python
- Django

### Frontend

- HTML
- CSS
- Bootstrap
- Tailwind CSS

### Database

- SQLite (Development)
- PostgreSQL (Production)

### Maps & Location

- Leaflet.js
- OpenStreetMap

### Image Processing

- Pillow
- OpenCV

### Deployment

- GitHub
- Render
- PostgreSQL
- WhiteNoise
- Gunicorn

---

## 📂 Project Workflow

```text
Citizen
   │
   ▼
Submit Waste Report
(Image + Location)
   │
   ▼
Automatically Assigned
to Municipality
   │
   ▼
Municipality Officer
Reviews Report
   │
   ▼
Assigns Worker
   │
   ▼
Worker Completes Task
   │
   ▼
Uploads Completion
Image & Notes
   │
   ▼
Report Marked Resolved
```

---

## 📸 Major Modules

- Authentication System
- Custom User Roles
- Waste Reporting
- Municipality Management
- Worker Management
- Notification System
- Email Integration
- Live Location Detection
- Report Tracking
- Dashboard Analytics

---

## 🔒 User Roles

| Role | Permissions |
|------|-------------|
| Public | Submit and Track Reports |
| Municipality | Manage Reports & Assign Workers |
| Worker | Complete Assigned Tasks |
| Admin | Full System Control |

---


## ⚙ Installation

Clone the repository

```bash
git clone https://github.com/Mrincxyl/Community_Waste_Management_System.git
```

Navigate to the project

```bash
cd Community_Waste_Management_System
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run migrations

```bash
python manage.py migrate
```

Start the development server

```bash
python manage.py runserver
```

---

## 🌐 Deployment

The application is configured for deployment using:

- Render
- PostgreSQL
- Gunicorn
- WhiteNoise

---

## 👨‍💻 Developed By

**Raihanxsk**

B.Tech Computer Science & Engineering (Data Science)

Brainware University

GitHub: https://github.com/Mrincxyl

---

## ⭐ Future Enhancements

- AI-based Waste Classification
- Real-time Worker Tracking
- SMS Notifications
- Mobile Application
- Smart Waste Analytics
- Digital Twin Integration

---

## 📜 License

This project is developed for educational, internship, and research purposes.
