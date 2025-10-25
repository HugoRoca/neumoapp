

# Neumoapp API - Medical Appointment Management System

REST API developed with FastAPI for medical appointment management, allowing patients to schedule, consult and manage their appointments with different medical specialties.

## 🏗️ Architecture

This project follows **Clean Architecture** principles with separation into layers:
- **Controllers** - HTTP request handlers
- **Services** - Business logic
- **Repositories** - Data access layer
- **Models** - Database entities
- **Schemas** - Data validation and serialization

📖 See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## 🚀 Features

- ✅ JWT (JSON Web Tokens) authentication
- ✅ Patient registration and login with document number
- ✅ Personal appointments dashboard
- ✅ Medical specialties management
- ✅ Consultation rooms with M:N relationship to specialties
- ✅ Dynamic scheduling system (morning: 8-13h, afternoon: 14-18h)
- ✅ 20-minute time slots (5 per hour)
- ✅ Appointment scheduling with consultation room assignment
- ✅ Appointment cancellation with schedule release
- ✅ PostgreSQL database
- ✅ Automatic documentation with Swagger UI
- ✅ Clean Architecture with layered design

## 📋 Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- PostgreSQL 14.4 (included in docker-compose)

## 🛠️ Installation

### 1. Clone repository (or navigate to directory)

```bash
cd /Users/hugoroca/repositories/neumoapp/service
```

### 2. Start PostgreSQL database

```bash
docker-compose up -d
```

This will start PostgreSQL on port 5432 with these credentials:
- **User**: root
- **Password**: root
- **Database**: neumoapp_db

### 3. Create Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Verify/Configure environment variables

The `.env` file is configured with:

```env
DATABASE_URL=postgresql://root:root@localhost:5432/neumoapp_db
SECRET_KEY=neumoapp-secret-key-change-in-production-2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PROJECT_NAME=Neumoapp API
VERSION=1.0.0
```

### 6. Create database schema

```bash
psql -U root -d neumoapp_db -f database_schema.sql
```

This will create:
- All database tables
- 10 medical specialties
- 16 consultation rooms
- Functions, triggers, and views

### 7. Initialize sample data

```bash
python init_db.py
```

This will create:
- 5 test patients
- Sample appointments

### 8. Run the application

```bash
python main.py
```

The API will be available at: **http://localhost:3000**

## 📚 API Documentation

Once the application is running, you can access interactive documentation:

- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc

## 🗂️ Project Structure

```
service/
├── app/
│   ├── controllers/              # 🎮 Presentation Layer
│   │   ├── auth_controller.py         # Authentication endpoints
│   │   ├── patient_controller.py      # Patient endpoints
│   │   ├── specialty_controller.py    # Specialties endpoints
│   │   ├── schedule_controller.py     # Schedules endpoints
│   │   └── appointment_controller.py  # Appointments endpoints
│   ├── services/                 # 💼 Business Logic Layer
│   │   ├── auth_service.py            # Authentication logic
│   │   ├── patient_service.py         # Patient business logic
│   │   ├── specialty_service.py       # Specialties business logic
│   │   ├── schedule_service.py        # Schedules business logic
│   │   └── appointment_service.py     # Appointments business logic
│   ├── repositories/             # 🗄️ Data Access Layer
│   │   ├── patient_repository.py      # Patient CRUD operations
│   │   ├── specialty_repository.py    # Specialties CRUD operations
│   │   ├── schedule_repository.py     # Schedules CRUD operations
│   │   └── appointment_repository.py  # Appointments CRUD operations
│   ├── models/                   # 🗃️ Database Entities
│   │   ├── patient.py                 # Patient Entity
│   │   ├── specialty.py               # Specialty Entity
│   │   ├── schedule.py                # Schedule Entity
│   │   └── appointment.py             # Appointment Entity
│   ├── schemas/                  # 📋 DTOs / Validation
│   │   ├── patient.py                 # Patient Schemas
│   │   ├── specialty.py               # Specialty Schemas
│   │   ├── schedule.py                # Schedule Schemas
│   │   └── appointment.py             # Appointment Schemas
│   ├── core/                     # ⚙️ Configuration
│   │   ├── config.py                  # Application configuration
│   │   ├── security.py                # Security (JWT, hash)
│   │   └── dependencies.py            # Shared dependencies
│   └── database/                 # 🔌 Database Connection
│       └── base.py                    # SQLAlchemy setup
├── main.py                       # 🚀 Application entry point
├── init_db.py                    # DB initialization script
├── docker-compose.yml            # Docker configuration
├── requirements.txt              # Python dependencies
├── ARCHITECTURE.md               # Architecture documentation
└── README.md                     # This file
```

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. All endpoints (except `/auth/register` and `/auth/login`) require authentication.

### Authentication flow:

1. **Register a patient**: `POST /auth/register`
2. **Login**: `POST /auth/login` - Returns a JWT token
3. **Use the token**: Include in header `Authorization: Bearer <token>` in all requests

## 📍 Main Endpoints

### Authentication

- `POST /auth/register` - Register new patient
- `POST /auth/login` - Login
- `GET /auth/me` - Get authenticated patient profile

### Specialties

- `GET /specialties/` - List all specialties
- `GET /specialties/{id}` - Get a specialty
- `POST /specialties/` - Create specialty (admin)

### Consultation Rooms

- `GET /consultation-rooms/` - List all consultation rooms
- `GET /consultation-rooms/by-specialty/{id}` - Get rooms for a specialty
- `GET /consultation-rooms/{id}` - Get room details
- `POST /consultation-rooms/` - Create consultation room (admin)

### Available Slots

- `GET /slots/available` - Get available time slots
  - Parameters: `specialty_id`, `date`, `shift` (required)

### Appointments

- `POST /appointments/` - Book an appointment
- `GET /appointments/my-appointments` - View my appointments (Dashboard)
- `GET /appointments/{id}` - View appointment details
- `PATCH /appointments/{id}` - Update appointment status/observations
- `DELETE /appointments/{id}` - Cancel an appointment

## 📝 Usage Examples

### 1. Register a patient

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "document_number": "12345678",
    "lastname": "Pérez",
    "firstname": "Juan",
    "date_birth": "1985-05-15",
    "gender": "Male",
    "address": "Av. Example 123",
    "phone": "987654321",
    "email": "juan@example.com",
    "civil_status": "Married",
    "password": "password123"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "document_number": "12345678",
    "password": "password123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. List specialties

```bash
curl -X GET "http://localhost:8000/specialties/" \
  -H "Authorization: Bearer <your-token>"
```

### 4. Query available slots

```bash
curl -X GET "http://localhost:3000/slots/available?specialty_id=1&date=2024-10-30&shift=morning" \
  -H "Authorization: Bearer <your-token>"
```

### 5. Book an appointment

```bash
curl -X POST "http://localhost:3000/appointments/" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "specialty_id": 1,
    "consultation_room_id": 1,
    "appointment_date": "2024-10-30",
    "start_time": "08:00:00",
    "shift": "morning",
    "reason": "Routine checkup"
  }'
```

### 6. View my appointments (Dashboard)

```bash
curl -X GET "http://localhost:3000/appointments/my-appointments" \
  -H "Authorization: Bearer <your-token>"
```

### 7. Cancel an appointment

```bash
curl -X DELETE "http://localhost:3000/appointments/1" \
  -H "Authorization: Bearer <your-token>"
```

## 🗄️ Database Model

### Main tables:

1. **patients**
   - id, document_number (unique), lastname, firstname, date_birth, gender, address, phone, email, civil_status, password_hash, active

2. **specialties**
   - id, name (unique), description, active

3. **consultation_rooms**
   - id, room_number (unique), name, floor, building, description, active

4. **specialty_consultation_rooms** (M:N)
   - specialty_id, consultation_room_id

5. **appointments**
   - id, patient_id, specialty_id, consultation_room_id, appointment_date, start_time, end_time, shift, status, reason, observations

### Relationships:
- One patient can have many appointments
- One specialty can have many consultation rooms (M:N)
- One consultation room can serve many specialties (M:N)
- One appointment belongs to a patient, specialty, and consultation room

### Key Features:
- ✅ **Dynamic scheduling** - No pre-generated schedules table
- ✅ **Flexible room assignment** - Rooms can be shared between specialties
- ✅ **Automatic slot generation** - 20-minute slots during working hours
- ✅ **Weekday validation** - Monday to Friday only

## 👥 Test Patients

After running `init_db.py`:

| Document | Password | Name |
|----------|----------|------|
| 12345678 | password123 | Juan Pérez |
| 87654321 | password123 | María González |
| 11111111 | password123 | Pedro Rodríguez |
| 22222222 | password123 | Ana Martínez |

## 🔧 Useful Commands

### View PostgreSQL logs
```bash
docker-compose logs -f postgres
```

### Stop database
```bash
docker-compose down
```

### Clean database (deletes data)
```bash
docker-compose down -v
docker-compose up -d
python init_db.py
```

### Run in development mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🛡️ Security

- Passwords are stored hashed with bcrypt
- JWT tokens expire in 30 minutes (configurable)
- Data validation with Pydantic
- SQL injection protection with SQLAlchemy ORM

## 📦 Technologies Used

- **FastAPI** - Modern and fast web framework
- **SQLAlchemy** - Python ORM
- **PostgreSQL** - Relational database
- **Pydantic** - Data validation
- **JWT** - Token-based authentication
- **Uvicorn** - ASGI server
- **Docker** - Containerization

## 🚀 Production Deployment

For production, consider:

1. Change `SECRET_KEY` in environment variables
2. Configure `allow_origins` in CORS with specific domains
3. Use production server (Gunicorn + Uvicorn workers)
4. Configure HTTPS
5. Implement rate limiting
6. Add proper logging
7. Use secure environment variables

## 📞 Support

For questions or issues, contact the development team.

## 📄 License

This project is under the MIT License.
