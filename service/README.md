# Neumoapp API - Medical Appointment Management System

REST API developed with FastAPI for medical appointment management, allowing patients to schedule, consult and manage their appointments at different hospitals with multiple medical specialties.

## 📑 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Features](#-features)
- [New Structure: Hospital → Specialties → Consultation Rooms](#-new-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [API Documentation](#-api-documentation)
- [API Endpoints](#-api-endpoints)
- [Booking Flow](#-booking-flow)
- [Usage Examples](#-usage-examples)
- [Database Model](#-database-model)
- [Test Patients](#-test-patients)
- [Technologies Used](#-technologies-used)

## ⚡ Quick Start

```bash
# 1. Start PostgreSQL
docker-compose up -d

# 2. Create virtual environment and install dependencies
python3 -m venv neumoapp
source neumoapp/bin/activate  # On Windows: neumoapp\Scripts\activate
pip install -r requirements.txt

# 3. Initialize database with sample data
python init_db.py

# 4. Run the API
uvicorn main:app --reload --host 0.0.0.0 --port 3000

# 5. Access Swagger UI
open http://localhost:3000/docs
```

**Test credentials:** DNI: `12345678` | Password: `password123`

## 🏗️ Architecture

This project follows **Clean Architecture** principles with separation into layers:

### Layer Structure
```
app/
├── controllers/     # HTTP request handlers (FastAPI routes)
├── services/        # Business logic layer
├── repositories/    # Data access layer
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic validation schemas
├── core/            # Configuration, security, dependencies
└── database/        # Database connection
```

### Key Principles
- **Separation of Concerns**: Each layer has a single responsibility
- **Dependency Injection**: Services receive dependencies via constructors
- **Independent of Frameworks**: Business logic doesn't depend on FastAPI
- **Testable**: Easy to mock dependencies for unit testing

📖 See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## 🚀 Features

- ✅ JWT (JSON Web Tokens) authentication
- ✅ Patient registration and login with document number
- ✅ **Multi-hospital system** - Manage multiple hospitals/clinics
- ✅ **Hospital → Specialties hierarchy** - Each hospital offers specific specialties
- ✅ **Specialties → Consultation Rooms** - Rooms can serve multiple specialties
- ✅ **Dynamic slot generation** - No pre-generated schedules
- ✅ Medical specialties management
- ✅ Consultation rooms with M:N relationship to specialties
- ✅ Intelligent booking flow with hospital selection first
- ✅ Real-time availability checking
- ✅ 20-minute time slots (morning: 8AM-1PM, afternoon: 2PM-6PM)
- ✅ Appointment scheduling with automatic validations
- ✅ Appointment cancellation with schedule release
- ✅ PostgreSQL database with advanced views and functions
- ✅ Automatic documentation with Swagger UI
- ✅ Clean Architecture with layered design

## 🏥 New Structure

### Hospital → Specialties → Consultation Rooms

The system now follows a hierarchical structure:

```
Hospital (Hospital Nacional Rebagliati)
  ├── Specialty (Cardiología)
  │     ├── Room 1 (R-CARD-201)
  │     └── Room 2 (R-CARD-202)
  ├── Specialty (Medicina General)
  │     ├── Room 1 (R-GRAL-101)
  │     ├── Room 2 (R-GRAL-102)
  │     └── Room 3 (R-GRAL-103)
  └── ...
```

### Key Relationships

1. **Hospital ↔ Specialty** (Many-to-Many)
   - A hospital offers multiple specialties
   - A specialty can be offered by multiple hospitals
   - Managed via `hospital_specialties` table

2. **Hospital → Consultation Room** (One-to-Many)
   - A consultation room belongs to exactly one hospital
   - A hospital has multiple consultation rooms

3. **Specialty ↔ Consultation Room** (Many-to-Many)
   - A consultation room can serve multiple specialties
   - A specialty uses multiple consultation rooms
   - Managed via `specialty_consultation_rooms` table

### Why This Structure?

- **Realistic**: Mirrors real-world hospital organization
- **Flexible**: Easy to add new hospitals or reassign specialties
- **Scalable**: Supports multi-location healthcare networks
- **Better UX**: Patients select hospital first, then see relevant options

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
python3 -m venv neumoapp
source neumoapp/bin/activate  # On Windows: neumoapp\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Initialize database with sample data

```bash
python init_db.py
```

This will create:
- 5 sample patients
- 10 medical specialties
- 3 hospitals (Rebagliati, Almenara, San Felipe)
- Hospital-specialty assignments
- 25+ consultation rooms across hospitals
- Specialty-room assignments
- 5 sample appointments

### 6. Run the API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

The API will be available at: `http://localhost:3000`

### 7. Access API Documentation

- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc

## 📚 API Documentation

Interactive documentation is available at:
- **Swagger UI**: http://localhost:3000/docs (try out endpoints)
- **ReDoc**: http://localhost:3000/redoc (cleaner documentation view)

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/auth/register` | Register new patient | ❌ |
| `POST` | `/auth/login` | Login with document number & password | ❌ |

### Patients

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/patients/me` | Get current patient profile | ✅ |
| `PUT` | `/patients/me` | Update patient profile | ✅ |

### Hospitals

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/hospitals` | List all hospitals | ✅ |
| `GET` | `/hospitals/{id}` | Get hospital details | ✅ |
| `GET` | `/hospitals/{id}/specialties` | **Get specialties offered by hospital** | ✅ |
| `GET` | `/hospitals/{id}/with-specialties` | Get hospital with specialty list | ✅ |
| `POST` | `/hospitals` | Create hospital (admin) | ✅ |
| `PATCH` | `/hospitals/{id}` | Update hospital (admin) | ✅ |
| `DELETE` | `/hospitals/{id}` | Deactivate hospital (admin) | ✅ |
| `POST` | `/hospitals/{id}/specialties` | Assign specialty to hospital (admin) | ✅ |
| `DELETE` | `/hospitals/{id}/specialties/{specialty_id}` | Remove specialty from hospital (admin) | ✅ |

### Specialties

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/specialties` | List all specialties | ✅ |
| `GET` | `/specialties/{id}` | Get specialty details | ✅ |
| `POST` | `/specialties` | Create specialty (admin) | ✅ |

### Consultation Rooms

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/consultation-rooms` | List all rooms | ✅ |
| `GET` | `/consultation-rooms/{id}` | Get room details | ✅ |
| `GET` | `/consultation-rooms/by-specialty/{specialty_id}` | Get rooms by specialty | ✅ |
| `GET` | `/consultation-rooms/by-hospital-and-specialty` | **Get rooms by hospital & specialty** | ✅ |
| `POST` | `/consultation-rooms` | Create room (admin) | ✅ |
| `PATCH` | `/consultation-rooms/{id}` | Update room (admin) | ✅ |

**Query Parameters for `/by-hospital-and-specialty`:**
- `hospital_id` (required): Hospital ID
- `specialty_id` (required): Specialty ID

### Available Slots

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/slots/available` | **Get all time slots (available/occupied)** | ✅ |

**Query Parameters:**
- `hospital_id` (required): Hospital ID
- `specialty_id` (required): Specialty ID
- `date` (required): Date (YYYY-MM-DD)
- `shift` (required): "morning" or "afternoon"
- `room_id` (optional): Filter by specific consultation room

### Appointments

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/appointments` | **Book appointment** | ✅ |
| `GET` | `/appointments/my-appointments` | Get my appointments | ✅ |
| `GET` | `/appointments/upcoming` | Get upcoming appointments | ✅ |
| `GET` | `/appointments/{id}` | Get appointment details | ✅ |
| `PATCH` | `/appointments/{id}` | Update appointment | ✅ |
| `DELETE` | `/appointments/{id}` | Cancel appointment | ✅ |

## 🔄 Booking Flow

The new booking flow follows these steps:

### Step 1: Select Hospital
```bash
GET /hospitals
```
**Response:** List of available hospitals

### Step 2: Select Specialty
```bash
GET /hospitals/{hospital_id}/specialties
```
**Response:** Specialties offered by that hospital with room count

### Step 3: View Consultation Rooms (Optional)
```bash
GET /consultation-rooms/by-hospital-and-specialty?hospital_id=1&specialty_id=2
```
**Response:** List of consultation rooms for that hospital and specialty

### Step 4: Check Time Slots
```bash
# Get all slots (available and occupied) for all rooms
GET /slots/available?hospital_id=1&specialty_id=2&date=2024-11-15&shift=morning

# Get slots for specific room (optional)
GET /slots/available?hospital_id=1&specialty_id=2&date=2024-11-15&shift=morning&room_id=5
```
**Response:** All time slots with `available: true/false` indicating if slot is free or booked

### Step 5: Book Appointment
```bash
POST /appointments
Body: {
  "specialty_id": 2,
  "consultation_room_id": 5,
  "appointment_date": "2024-11-15",
  "start_time": "09:00:00",
  "shift": "morning",
  "reason": "Consulta de control"
}
```
**Response:** Confirmed appointment details

## 💡 Usage Examples

### 1. Register a new patient

```bash
POST http://localhost:3000/auth/register
Content-Type: application/json

{
  "document_number": "99999999",
  "last_name": "Silva",
  "first_name": "Roberto",
  "birth_date": "1988-06-15",
  "gender": "M",
  "phone": "999111222",
  "email": "roberto.silva@example.com",
  "address": "Av. Ejemplo 789",
  "password": "securepass123"
}
```

### 2. Login

```bash
POST http://localhost:3000/auth/login
Content-Type: application/x-www-form-urlencoded

username=12345678&password=password123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
  "token_type": "bearer"
}
```

### 3. Get all hospitals

```bash
GET http://localhost:3000/hospitals
Authorization: Bearer <your_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Hospital Nacional Rebagliati",
    "code": "HNR",
    "address": "Av. Rebagliati 490, Jesús María",
    "district": "Jesús María",
    "city": "Lima",
    "phone": "01-2654901",
    "email": "contacto@rebagliati.gob.pe",
    "active": true,
    "created_at": "2024-10-26T10:00:00"
  },
  ...
]
```

### 4. Get specialties for a hospital

```bash
GET http://localhost:3000/hospitals/1/specialties
Authorization: Bearer <your_token>
```

**Response:**
```json
[
  {
    "id": 2,
    "name": "Cardiología",
    "description": "Especialista en enfermedades del corazón",
    "active": true,
    "available_rooms": 2,
    "created_at": "2024-10-26T10:00:00"
  },
  ...
]
```

### 5. Get consultation rooms (optional)

```bash
# Get all rooms for a hospital and specialty
GET http://localhost:3000/consultation-rooms/by-hospital-and-specialty?hospital_id=1&specialty_id=2
Authorization: Bearer <your_token>
```

**Response:**
```json
[
  {
    "id": 4,
    "room_number": "R-CARD-201",
    "name": "Consultorio Cardiología 1",
    "floor": 2,
    "building": "A",
    "description": "Consultorio equipado para cardiología",
    "active": true,
    "hospital_id": 1,
    "created_at": "2024-10-26T10:00:00",
    "updated_at": "2024-10-26T10:00:00"
  },
  {
    "id": 5,
    "room_number": "R-CARD-202",
    "name": "Consultorio Cardiología 2",
    "floor": 2,
    "building": "A",
    "description": "Consultorio equipado para cardiología",
    "active": true,
    "hospital_id": 1,
    "created_at": "2024-10-26T10:00:00",
    "updated_at": "2024-10-26T10:00:00"
  }
]
```

### 6. Check available slots

```bash
# Get all available slots for hospital and specialty
GET http://localhost:3000/slots/available?hospital_id=1&specialty_id=2&date=2024-11-18&shift=morning
Authorization: Bearer <your_token>

# Get slots for a specific consultation room (optional)
GET http://localhost:3000/slots/available?hospital_id=1&specialty_id=2&date=2024-11-18&shift=morning&room_id=4
Authorization: Bearer <your_token>
```

**Response:** (Returns ALL slots with `available` field indicating status)
```json
{
  "specialty_id": 2,
  "specialty_name": "Cardiología",
  "date": "2024-11-18",
  "shift": "morning",
  "slots": [
    {
      "start_time": "08:00:00",
      "end_time": "08:20:00",
      "consultation_room": {
        "id": 4,
        "room_number": "R-CARD-201",
        "name": "Consultorio Cardiología 1"
      },
      "available": true
    },
    {
      "start_time": "08:20:00",
      "end_time": "08:40:00",
      "consultation_room": {
        "id": 4,
        "room_number": "R-CARD-201",
        "name": "Consultorio Cardiología 1"
      },
      "available": false
    },
    {
      "start_time": "08:40:00",
      "end_time": "09:00:00",
      "consultation_room": {
        "id": 5,
        "room_number": "R-CARD-202",
        "name": "Consultorio Cardiología 2"
      },
      "available": true
    },
    ...
  ]
}
```

### 7. Book an appointment

```bash
POST http://localhost:3000/appointments
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "specialty_id": 2,
  "consultation_room_id": 4,
  "appointment_date": "2024-11-18",
  "start_time": "08:00:00",
  "shift": "morning",
  "reason": "Control de presión arterial"
}
```

**Response:**
```json
{
  "id": 6,
  "patient_id": 1,
  "specialty_id": 2,
  "consultation_room_id": 4,
  "appointment_date": "2024-11-18",
  "start_time": "08:00:00",
  "end_time": "08:20:00",
  "shift": "morning",
  "status": "pending",
  "reason": "Control de presión arterial",
  "created_at": "2024-10-26T14:30:00",
  "updated_at": "2024-10-26T14:30:00"
}
```

### 7. View my appointments

```bash
GET http://localhost:3000/appointments/my-appointments
Authorization: Bearer <your_token>
```

### 8. Cancel an appointment

```bash
DELETE http://localhost:3000/appointments/6
Authorization: Bearer <your_token>
```

## 🗄️ Database Model

### Entity Relationship Diagram

```
patients                    appointments               specialties
+----------------+         +------------------+       +-----------------+
| id (PK)        |    ┌────| id (PK)          |       | id (PK)         |
| document_number|    │    | patient_id (FK)  |───────| name            |
| last_name      |    │    | specialty_id (FK)|───┐   | description     |
| first_name     |────┘    | consultation_room|   └───| active          |
| birth_date     |         | appointment_date |       +-----------------+
| gender         |         | start_time       |              │
| email          |         | end_time         |              │ M:N
| password_hash  |         | shift            |              │
+----------------+         | status           |       hospital_specialties
                           | reason           |       +-------------------+
                           +------------------+       | hospital_id (FK)  |
                                    │                 | specialty_id (FK) |
                                    │                 | active            |
                                    │                 +-------------------+
                                    │                        │
                           consultation_rooms                │
                           +-------------------+             │
                      ┌────| id (PK)           |             │
                      │    | hospital_id (FK)  |─────────────┘
                      │    | room_number       |             │
                      │    | name              |             │
                      │    | floor             |             │
                      │    | building          |             │
                      │    | active            |             │
                      │    +-------------------+             │
                      │             │                        │
                      │             │ M:N                    │
                      │             │                        │
                      │    specialty_consultation_rooms     │
                      │    +---------------------------+    │
                      │    | specialty_id (FK)         |────┘
                      └────| consultation_room_id (FK) |
                           +---------------------------+

                           hospitals
                           +-----------------+
                           | id (PK)         |
                           | name            |
                           | code            |
                           | address         |
                           | district        |
                           | city            |
                           | phone           |
                           | email           |
                           | active          |
                           +-----------------+
```

### Key Tables

#### `patients`
- User authentication and profile data
- Each patient can have multiple appointments

#### `hospitals`
- Healthcare facilities where services are provided
- Can offer multiple specialties

#### `specialties`
- Medical specialties (Cardiology, Pediatrics, etc.)
- Can be offered by multiple hospitals
- Can use multiple consultation rooms

#### `hospital_specialties`
- M:N relationship between hospitals and specialties
- Defines which specialties are offered at which hospitals

#### `consultation_rooms`
- Physical consultation rooms in hospitals
- Belong to exactly one hospital
- Can serve multiple specialties

#### `specialty_consultation_rooms`
- M:N relationship between specialties and consultation rooms
- Defines which rooms are used for which specialties

#### `appointments`
- Scheduled appointments
- Links patients, specialties, and consultation rooms
- Stores date, time, shift, and status

### Database Views

The system includes several database views for optimized queries:

- `v_hospitals_with_stats` - Hospitals with aggregated statistics
- `v_hospital_specialties` - Specialties available per hospital
- `v_consultation_rooms_with_info` - Rooms with hospital and specialty info
- `v_upcoming_appointments` - Upcoming appointments with full details
- `v_room_usage_stats` - Usage statistics per consultation room

## 👥 Test Patients

The database is pre-populated with test patients:

| Document Number | Name | Email | Password |
|----------------|------|-------|----------|
| 12345678 | Juan Pérez | juan.perez@example.com | password123 |
| 87654321 | María González | maria.gonzalez@example.com | password123 |
| 11111111 | Pedro Rodríguez | pedro.rodriguez@example.com | password123 |
| 22222222 | Ana Martínez | ana.martinez@example.com | password123 |
| 33333333 | Carlos López | carlos.lopez@example.com | password123 |

## 🏥 Sample Hospitals

| Code | Name | Specialties | Rooms |
|------|------|-------------|-------|
| HNR | Hospital Nacional Rebagliati | 10 | 14 |
| HAL | Hospital Almenara | 9 | 7 |
| CSF | Clínica San Felipe | 6 | 4 |

## ⚙️ Business Rules

### Scheduling Rules
- **Slots**: 20 minutes each (5 per hour)
- **Morning shift**: 8:00 AM - 1:00 PM (15 slots)
- **Afternoon shift**: 2:00 PM - 6:00 PM (12 slots)
- **Working days**: Monday to Friday only
- **Real-time validation**: No double-booking
- **Dynamic generation**: Slots generated on-demand

### Booking Rules
1. Patient must be authenticated
2. Hospital must offer the selected specialty
3. Consultation room must:
   - Belong to the selected hospital
   - Be assigned to the selected specialty
   - Be available at the requested time
4. Appointment must be:
   - On a weekday (Monday-Friday)
   - In the future
   - Within valid time ranges

## 🛠️ Technologies Used

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type hints
- **PostgreSQL** - Relational database
- **JWT** - Authentication tokens
- **Passlib** - Password hashing
- **Uvicorn** - ASGI server
- **Python 3.10+** - Programming language
- **Docker** - Containerization

## 📝 Environment Variables

The application uses the following environment variables (defined in `.env`):

```env
DATABASE_URL=postgresql://root:root@localhost:5432/neumoapp_db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
PROJECT_NAME=Neumoapp API
VERSION=4.0
```

## 🔐 Security

- Passwords are hashed using bcrypt (via passlib)
- JWT tokens for authentication
- Token expiration: 30 minutes
- Protected endpoints require valid Bearer token
- SQL injection protection via SQLAlchemy ORM

## 📊 Database Functions

The schema includes useful PostgreSQL functions:

- `check_slot_availability()` - Check if a time slot is available
- `is_weekday()` - Validate if date is Monday-Friday
- `get_hospital_specialties()` - Get specialties offered by a hospital
- `get_available_rooms_for_specialty()` - Get rooms for a specialty at a hospital

## 🧪 Testing

To test the API:

1. Use Swagger UI at `http://localhost:3000/docs`
2. Click "Authorize" and login with test credentials
3. Try the endpoints in the booking flow order
4. Or use Postman/curl with the provided examples

## 📦 Project Structure

```
service/
├── app/
│   ├── controllers/          # API endpoints
│   │   ├── auth_controller.py
│   │   ├── patient_controller.py
│   │   ├── hospital_controller.py
│   │   ├── specialty_controller.py
│   │   ├── consultation_room_controller.py
│   │   ├── slot_controller.py
│   │   └── appointment_controller.py
│   ├── services/             # Business logic
│   │   ├── auth_service.py
│   │   ├── patient_service.py
│   │   ├── hospital_service.py
│   │   ├── specialty_service.py
│   │   ├── consultation_room_service.py
│   │   ├── slot_service.py
│   │   └── appointment_service.py
│   ├── repositories/         # Data access
│   │   ├── patient_repository.py
│   │   ├── hospital_repository.py
│   │   ├── specialty_repository.py
│   │   ├── consultation_room_repository.py
│   │   └── appointment_repository.py
│   ├── models/               # SQLAlchemy models
│   │   ├── patient.py
│   │   ├── hospital.py
│   │   ├── specialty.py
│   │   ├── consultation_room.py
│   │   └── appointment.py
│   ├── schemas/              # Pydantic schemas
│   │   ├── patient.py
│   │   ├── hospital.py
│   │   ├── specialty.py
│   │   ├── consultation_room.py
│   │   └── appointment.py
│   ├── core/                 # Configuration
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   └── database/             # DB connection
│       └── base.py
├── scripts/
│   └── database_schema.sql   # Complete DB schema
├── main.py                   # FastAPI application
├── init_db.py                # Database initialization
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # PostgreSQL container
└── README.md                 # This file
```

## 🚀 Next Steps

Potential improvements:
- [ ] Admin panel for hospital management
- [ ] Email notifications for appointments
- [ ] SMS reminders
- [ ] Video consultation integration
- [ ] Doctor/Staff management
- [ ] Medical records
- [ ] Prescription management
- [ ] Payment integration
- [ ] Multi-language support

## 📄 License

This project is for educational/demonstration purposes.

## 👨‍💻 Author

Developed as part of the Neumoapp project.

---

**API Base URL**: `http://localhost:3000`  
**Documentation**: `http://localhost:3000/docs`  
**Version**: 4.0  
**Last Updated**: October 2024
