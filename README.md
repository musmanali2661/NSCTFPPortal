# NSCTFPPortal — NSCT Focal Person Portal

A **Command Center** for the University of Gujrat's NSCT (National Skills Certification Test) Focal Person. This portal automates student data management, discrepancy detection, helpdesk ticketing, and logistics planning for the HEC examination process.

---

## Features

### A. Intelligent Data Management
- **Smart Bulk Importer** — Upload `.csv` or `.xlsx` student lists; system auto-maps columns to HEC/NSCT required fields
- **Discrepancy Highlight Engine** — Automatically flags placeholder CNICs (`00000-0000000-0`), invalid DOB/GPA formats, and duplicate entries
- **Real-time Progress Tracker** — Dashboard showing Uploaded vs. Registered vs. Validated per department

### B. Communication & Helpdesk
- **Support Ticket System** — Student query management with AI-generated reply suggestions
- **Category Auto-classification** — Tickets classified as Transport, Login, Data Correction, or General Info

### C. Logistics & Transport Module
- **Transport Flag** — Students requesting Gujrat bus transport are flagged for route planning

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI (Python 3.11) |
| **Frontend** | React 18 + TypeScript |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **AI Engine** | FuzzyWuzzy + OpenAI (optional) |
| **Containerization** | Docker + Docker Compose |

---

## Database Schema

- **`departments`** — CS, IT, SE departments with coordinator links
- **`staff`** — Admin (Focal Person) and Coordinator roles
- **`students`** — Master student records (reg_no, CNIC, GPA, batch type, status)
- **`data_discrepancies`** — Flagged data issues (Placeholder_Value, Format_Mismatch, Duplicate)
- **`support_tickets`** — Student helpdesk queries with AI reply suggestions
- **`question_bank`** — GIFT-format question management

---

## Quick Start (Docker)

```bash
# Clone and start all services
git clone https://github.com/musmanali2661/NSCTFPPortal.git
cd NSCTFPPortal
docker-compose up --build
```

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs

### Default Admin Login
| Field | Value |
|-------|-------|
| Email | `admin@uog.edu.pk` |
| Password | `admin123` |

---

## Local Development (Without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000 npm start
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/login` | Get JWT token |
| `GET` | `/students` | List students (with filters) |
| `POST` | `/students` | Create student |
| `PUT` | `/students/{id}` | Update student |
| `DELETE` | `/students/{id}` | Delete student |
| `GET` | `/departments` | List departments |
| `GET` | `/discrepancies` | List discrepancies |
| `PUT` | `/discrepancies/{id}/resolve` | Resolve discrepancy |
| `GET` | `/tickets` | List support tickets |
| `POST` | `/tickets/{id}/ai-reply` | Generate AI reply |
| `POST` | `/uploads/csv` | Bulk upload CSV/XLSX |
| `GET` | `/uploads/template` | Download CSV template |
| `GET` | `/dashboard/stats` | Dashboard statistics |
| `GET` | `/question-bank` | List questions |

Full interactive API documentation is available at `http://localhost:8000/docs`.

---

## CSV Upload Format

Download the template at `/uploads/template`. Required columns:

| Column | Description |
|--------|-------------|
| `reg_no` | Registration number (unique) |
| `full_name` | Student full name |
| `father_name` | Father's name |
| `cnic` | CNIC (format: 00000-0000000-0) |
| `dob` | Date of birth (YYYY-MM-DD) |
| `gender` | Male / Female / Other |
| `email` | Student email |
| `mobile_number` | Mobile number |
| `department_id` | Department ID (1=CS, 2=IT, 3=SE) |
| `batch_type` | Morning / Evening / Lateral |
| `semester_no` | 7 or 8 |
| `gpa` | GPA (numeric) |
| `cgpa` | CGPA (numeric) |
| `transport_required` | true / false |

---

## Discrepancy Types

| Error Type | Description | Severity |
|-----------|-------------|----------|
| `Placeholder_Value` | CNIC is `00000-0000000-0` | Critical |
| `Format_Mismatch` | Invalid CNIC format | High |
| `Format_Mismatch` | Invalid DOB format | High |
| `Format_Mismatch` | Non-numeric GPA/CGPA | High |
| `Format_Mismatch` | Missing required fields | High |
| `Duplicate` | Duplicate CNIC | Critical |
| `Duplicate` | Duplicate reg_no | Critical |

---

## Project Roadmap

- [x] **Stage 1 (Data Clean):** CSV upload + Discrepancy Dashboard ← *March 12 deadline*
- [x] **Stage 2 (Support):** AI Chatbot / Ticket system ← *March 20 portal lock*
- [ ] **Stage 3 (Logistics):** Transport route optimizer + exam conflict checker

---

## Security Notes

- Change `SECRET_KEY` in `.env` before production deployment
- Use PostgreSQL in production (set `DATABASE_URL` to a PostgreSQL connection string)
- Configure `OPENAI_API_KEY` in `.env` for full AI reply generation