# Diagrama de clases — Neumoapp (backend)

Documentación del modelo de dominio persistido con SQLAlchemy y de la capa de servicios/repositorios que lo usa. Código fuente bajo `service/app/`.

## 1. Modelo de dominio (ORM)

Entidades en `app/models/`. Todas heredan de `Base` definido en `app/database/base.py` (metadata SQLAlchemy).

### Relaciones

| Relación | Tipo | Detalle |
|----------|------|---------|
| Patient ↔ Appointment | 1:N | Un paciente tiene muchas citas. |
| Specialty ↔ Appointment | 1:N | Una especialidad en muchas citas. |
| ConsultationRoom ↔ Appointment | 1:N | Un consultorio en muchas citas. |
| Hospital ↔ ConsultationRoom | 1:N | Un hospital tiene muchos consultorios. |
| Hospital ↔ Specialty | N:M | Tabla de unión `hospital_specialties` (`app/models/hospital.py`). |
| Specialty ↔ ConsultationRoom | N:M | Tabla de unión `specialty_consultation_rooms` (`app/models/consultation_room.py`). |

### Notas

- En la base de datos, `appointments.status` es texto; en código existen los enums `AppointmentStatus` y `ShiftType` en `app/models/appointment.py` como referencia semántica para valores permitidos.
- Las tablas de asociación incluyen columnas extra donde aplica (por ejemplo `active` y `created_at` en `hospital_specialties`).

### Diagrama (Mermaid)

```mermaid
classDiagram
    direction TB

    class Base {
        <<declarative_base>>
    }

    class AppointmentStatus {
        <<enumeration>>
        PENDING
        CONFIRMED
        RESCHEDULED
        CANCELLED
        COMPLETED
    }

    class ShiftType {
        <<enumeration>>
        MORNING
        AFTERNOON
    }

    class Patient {
        +int id
        +str document_number
        +str last_name
        +str first_name
        +date birth_date
        +str gender
        +str address
        +str phone
        +str email
        +str password_hash
        +bool active
        +datetime created_at
        +datetime updated_at
    }

    class Hospital {
        +int id
        +str name
        +str code
        +str address
        +str district
        +str city
        +str phone
        +str email
        +str description
        +bool active
        +datetime created_at
        +datetime updated_at
    }

    class Specialty {
        +int id
        +str name
        +str description
        +bool active
        +datetime created_at
        +datetime updated_at
    }

    class ConsultationRoom {
        +int id
        +int hospital_id
        +str room_number
        +str name
        +str floor
        +str building
        +str description
        +bool active
        +datetime created_at
        +datetime updated_at
    }

    class Appointment {
        +int id
        +int patient_id
        +int specialty_id
        +int consultation_room_id
        +date appointment_date
        +time start_time
        +time end_time
        +str shift
        +str status
        +str reason
        +str observations
        +datetime created_at
        +datetime updated_at
    }

    class hospital_specialties {
        <<association_table>>
        +int hospital_id PK_FK
        +int specialty_id PK_FK
        +bool active
        +datetime created_at
    }

    class specialty_consultation_rooms {
        <<association_table>>
        +int specialty_id PK_FK
        +int consultation_room_id PK_FK
        +datetime created_at
    }

    Base <|-- Patient
    Base <|-- Hospital
    Base <|-- Specialty
    Base <|-- ConsultationRoom
    Base <|-- Appointment

    Patient "1" --> "*" Appointment
    Specialty "1" --> "*" Appointment
    ConsultationRoom "1" --> "*" Appointment
    Hospital "1" --> "*" ConsultationRoom

    Hospital "1" --> hospital_specialties
    Specialty "1" --> hospital_specialties
    Specialty "1" --> specialty_consultation_rooms
    ConsultationRoom "1" --> specialty_consultation_rooms

    Appointment ..> AppointmentStatus : status
    Appointment ..> ShiftType : shift
```

## 2. Capa de aplicación (servicios y repositorios)

Los endpoints FastAPI (`app/controllers/`) construyen servicios pasando una `Session` de SQLAlchemy. Cada servicio de dominio compone el repositorio correspondiente (`app/repositories/`). Los DTO de request/response son esquemas Pydantic en `app/schemas/` (heredan de `BaseModel`); no son entidades ORM.

### Diagrama (Mermaid)

```mermaid
classDiagram
    direction LR

    class Settings {
        <<BaseSettings>>
        +DATABASE_URL
        +SECRET_KEY
        +JWT...
        +OPENAI_*
        +APP_TIMEZONE
    }

    class PatientRepository
    class HospitalRepository
    class SpecialtyRepository
    class ConsultationRoomRepository
    class AppointmentRepository

    class PatientService
    class AuthService
    class HospitalService
    class SpecialtyService
    class ConsultationRoomService
    class SlotService
    class AppointmentService
    class SchedulingWizardService
    class ChatToolExecutor

    PatientService *-- PatientRepository
    HospitalService *-- HospitalRepository
    SpecialtyService *-- SpecialtyRepository
    ConsultationRoomService *-- ConsultationRoomRepository
    AppointmentService *-- AppointmentRepository

    ChatToolExecutor *-- AppointmentService
    ChatToolExecutor *-- SlotService
    ChatToolExecutor *-- HospitalRepository
    ChatToolExecutor *-- SpecialtyRepository
    ChatToolExecutor *-- ConsultationRoomRepository

    Settings ..> ChatToolExecutor : settings globales
```

### Chat / OpenAI

- `app/services/openai_chat_service.py`: orquestación del chat (funciones de módulo, p. ej. `run_chat`), cliente OpenAI-compatible.
- `app/services/chat_tool_executor.py`: clase `ChatToolExecutor` — ejecuta herramientas del modelo delegando en servicios y repositorios existentes.
- `app/services/scheduling_wizard_service.py`: clase `SchedulingWizardService` — flujo asistido de agendamiento.

## 3. Cómo visualizar los diagramas

- **GitHub / GitLab**: el Markdown con bloques `mermaid` suele renderizarse en la vista del repositorio.
- **VS Code / Cursor**: extensión “Markdown Preview Mermaid Support” o similar.
- **Mermaid Live Editor**: https://mermaid.live (pegar el contenido de cada bloque).

## 4. Archivos de referencia

| Área | Ruta |
|------|------|
| Modelos | `service/app/models/` |
| Esquemas API | `service/app/schemas/` |
| Repositorios | `service/app/repositories/` |
| Servicios | `service/app/services/` |
| Controladores | `service/app/controllers/` |
| Base y sesión | `service/app/database/base.py` |
| Configuración | `service/app/core/config.py` |
