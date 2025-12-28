# Job Application Tracking System API

## Overview

This project is a **Job Application Tracking System (ATS) REST API** that manages the end-to-end hiring workflow. It goes beyond basic CRUD by implementing:

* A strict **application workflow state machine**
* **Role-Based Access Control (RBAC)**
* **Asynchronous email notifications** using background processing
* A complete **audit trail** of application stage changes

The system is designed to reflect real-world hiring processes used by HR platforms.

---

##  Tech Stack

* **Backend**: FastAPI (Python)
* **Database**: PostgreSQL + SQLAlchemy ORM
* **Authentication**: JWT (OAuth2 Password Flow)
* **Async Tasks**: Background worker (Celery / FastAPI BackgroundTasks)
* **Email**: SMTP (SendGrid optional)
* **API Docs**: Swagger / OpenAPI

---

##  User Roles & Permissions

### Candidate

* Register and login
* Apply for jobs
* View their own applications and current status

### Recruiter

* Create, update, delete jobs (company-specific)
* View and manage applications for jobs they own
* Change application stages

---

## 🔄 Application Workflow (State Machine)

Valid application stages:

```
Applied → Screening → Interview → Offer → Hired
```

Special rule:

```
Any stage → Rejected
```

### Rules Enforced

* ❌ Skipping stages is NOT allowed
* ❌ Direct `Applied → Hired` is invalid
* ✅ `Reject` is allowed from any stage

This logic is centralized in a dedicated **workflow service**, ensuring consistency.

---

## 🗂 Data Models

* **User**: id, name, email, password, role
* **Company**: id, name
* **Job**: id, title, description, status
* **Application**: id, job_id, candidate_id, stage
* **ApplicationHistory**: id, application_id, old_stage, new_stage

Every stage change is recorded in `ApplicationHistory` for auditing.

---

## ✉ Asynchronous Email Notifications

Emails are sent for:

* Successful job application submission
* Every application stage change
* New application notification to recruiter
* But it is not working properly because of the purchase of api is not working

### Key Design Point

Email sending is **decoupled** from API request handling:

* The API enqueues email tasks
* A background worker processes them
* API responses remain fast and non-blocking

> Redis/RabbitMQ can be plugged in without changing business logic. The async layer is fully decoupled.

---

##  Security Best Practices

* Passwords are hashed
* JWT tokens for authentication
* Environment variables for secrets
* Role and ownership checks on every protected endpoint

---

## Environment Variables (`.env`)

```env
DATABASE_URL=postgresql://postgres:Dileep%402025@localhost:5432/ats_db
SECRET_KEY=9f8d7c6b5a4e3d2c1b0a9e8f7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1
```

---

## ▶️ How to Run the Project

### 1️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/Scripts/activate
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Start PostgreSQL

* Start PostgreSQL from **Windows Services**
* Ensure database `ats_db` exists

### 4️⃣ Run Migrations / Create Tables

```bash
python app/create_tables.py
```

### 5️⃣ Start API Server

```bash
uvicorn app.main:app --reload
```

---

## 📄 API Documentation

Once the server is running:

* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## ✅ Expected Outcomes (Satisfied)

* ✔ Fully functional REST API
* ✔ Role-based access control
* ✔ Workflow state machine enforcement
* ✔ Asynchronous email notifications
* ✔ Complete audit trail (ApplicationHistory)
* ✔ Responsive API design
* ✔ Clean architecture and documentation

---

## 🚀 Future Enhancements

* Redis/RabbitMQ integration for task queue
* Company-level multi-tenancy isolation
* Admin dashboard
* Advanced analytics and reports

---

## 👨‍💻 Author

**DILEEP KUMAR REDDY SATHI**

B.Tech – Artificial Intelligence & Machine Learning

---

⭐ This project demonstrates real-world backend system design and workflow management.
