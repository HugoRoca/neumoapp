# 🏥 Cambios Implementados: Hospital → Especialidades → Consultorios

## 📋 Resumen

Se ha implementado una **nueva arquitectura jerárquica** donde:

```
Hospital → Especialidades → Consultorios
```

### Antes (Old Structure)
```
Consultorios ← Especialidades
```
- Los consultorios no pertenecían a ningún hospital
- No había concepto de hospital en el sistema

### Ahora (New Structure)
```
Hospital → Especialidades (M:N)
Hospital → Consultorios (1:N)
Consultorios ← Especialidades (M:N)
```
- Los hospitales ofrecen especialidades específicas
- Los consultorios pertenecen a un hospital
- Flujo de reserva: Seleccionar Hospital → Especialidad → Turno → Consultorio

## 🎯 Cambios Realizados

### 1. Base de Datos

#### Nuevas Tablas
- **`hospitals`**: Tabla de hospitales/clínicas
- **`hospital_specialties`**: Relación M:N entre hospitales y especialidades

#### Tablas Modificadas
- **`consultation_rooms`**: 
  - ✅ Agregado campo `hospital_id` (FK a hospitals)
  - ✅ Ahora pertenece a un hospital específico

#### Scripts SQL
- ✅ **`migration_hospital_specialties.sql`**: Script de migración para BD existente
- ✅ **`scripts/database_schema.sql`**: Esquema completo actualizado (v4.0)

#### Nuevas Vistas
- `v_hospitals_with_stats`: Hospitales con estadísticas
- `v_hospital_specialties`: Especialidades por hospital
- `v_consultation_rooms_with_info`: Consultorios con info de hospital
- Actualizadas: `v_upcoming_appointments`, `v_room_usage_stats`

#### Nuevas Funciones
- `get_hospital_specialties(hospital_id)`: Obtener especialidades de un hospital
- `get_available_rooms_for_specialty(hospital_id, specialty_id)`: Consultorios disponibles

### 2. Modelos (SQLAlchemy)

#### Nuevo Modelo
```python
# app/models/hospital.py
class Hospital(Base):
    __tablename__ = "hospitals"
    # ... campos ...
    
    # Relationships
    consultation_rooms = relationship("ConsultationRoom", back_populates="hospital")
    specialties = relationship("Specialty", secondary="hospital_specialties", 
                              back_populates="hospitals")
```

#### Tabla de Asociación
```python
# app/models/hospital.py
hospital_specialties = Table(
    'hospital_specialties',
    Base.metadata,
    Column('hospital_id', Integer, ForeignKey('hospitals.id')),
    Column('specialty_id', Integer, ForeignKey('specialties.id')),
    Column('active', Boolean, default=True),
    Column('created_at', DateTime)
)
```

#### Modelos Modificados
- **`Specialty`**: Agregada relación `hospitals`
- **`ConsultationRoom`**: Agregado campo `hospital_id` y relación `hospital`

### 3. Schemas (Pydantic)

#### Nuevos Schemas
```python
# app/schemas/hospital.py
class HospitalCreate(HospitalBase):
    specialty_ids: Optional[List[int]] = []  # Asignar especialidades al crear

class HospitalWithSpecialties(HospitalResponse):
    specialties: List[SpecialtySimple] = []

class AssignSpecialtyRequest(BaseModel):
    specialty_id: int

class RemoveSpecialtyRequest(BaseModel):
    specialty_id: int
```

```python
# app/schemas/specialty.py
class SpecialtyWithRoomCount(SpecialtyResponse):
    available_rooms: int = 0  # Para mostrar cantidad de consultorios
```

#### Schemas Modificados
- **`SpecialtyBase`**: Eliminado campo `consultation_rooms` (ya no es número fijo)
- **`ConsultationRoomBase`**: Agregado campo `hospital_id`

### 4. Repositorios

#### Nuevos Métodos en `HospitalRepository`
```python
def get_by_id_with_specialties(hospital_id: int) -> Optional[Hospital]
def get_specialties(hospital_id: int, active_only: bool = True) -> List[Specialty]
def has_specialty(hospital_id: int, specialty_id: int) -> bool
def add_specialty(hospital_id: int, specialty: Specialty) -> bool
def remove_specialty(hospital_id: int, specialty: Specialty) -> bool
```

#### Nuevos Métodos en `ConsultationRoomRepository`
```python
def get_by_hospital(hospital_id: int, active_only: bool = True) -> List[ConsultationRoom]
def get_by_hospital_and_specialty(hospital_id: int, specialty_id: int, 
                                   active_only: bool = True) -> List[ConsultationRoom]
```

### 5. Servicios

#### `HospitalService` - Nuevos Métodos
```python
def get_hospital_with_specialties(hospital_id: int) -> Hospital
def get_hospital_specialties(hospital_id: int) -> List[Specialty]
def assign_specialty_to_hospital(hospital_id: int, specialty_id: int) -> dict
def remove_specialty_from_hospital(hospital_id: int, specialty_id: int) -> dict
```

#### `SlotService` - Modificaciones
```python
# ANTES
def get_available_slots(specialty_id, date, shift) -> AvailableSlotsResponse

# AHORA
def get_available_slots(hospital_id, specialty_id, date, shift) -> AvailableSlotsResponse
# Filtra consultorios por hospital
```

#### `AppointmentService` - Validaciones Agregadas
```python
def book_appointment(...):
    # ... validaciones existentes ...
    
    # NUEVA VALIDACIÓN: Hospital debe ofrecer la especialidad
    if not self.hospital_repo.has_specialty(hospital.id, specialty.id):
        raise HTTPException(...)
```

### 6. Controladores (Endpoints)

#### Nuevos Endpoints de Hospitales

```python
# GET /hospitals
# → Lista todos los hospitales

# GET /hospitals/{id}
# → Detalle de un hospital

# GET /hospitals/{id}/specialties  ⭐ IMPORTANTE
# → Especialidades ofrecidas por el hospital
# → ESTE ES EL SEGUNDO PASO DEL FLUJO DE RESERVA

# GET /hospitals/{id}/with-specialties
# → Hospital con lista de especialidades

# POST /hospitals
# → Crear hospital (admin)

# POST /hospitals/{id}/specialties
# → Asignar especialidad a hospital (admin)

# DELETE /hospitals/{id}/specialties/{specialty_id}
# → Remover especialidad de hospital (admin)
```

#### Endpoint Modificado

```python
# GET /slots/available
# ANTES: ?specialty_id=1&date=2024-11-15&shift=morning
# AHORA: ?hospital_id=1&specialty_id=1&date=2024-11-15&shift=morning
#        ^^^^^^^^^^^^^^ NUEVO PARÁMETRO OBLIGATORIO
```

### 7. Datos de Prueba (`init_db.py`)

El script `init_db.py` ahora crea:

#### Hospitales
1. **Hospital Nacional Rebagliati (HNR)**
   - 10 especialidades
   - 14 consultorios

2. **Hospital Almenara (HAL)**
   - 9 especialidades
   - 7 consultorios

3. **Clínica San Felipe (CSF)**
   - 6 especialidades
   - 4 consultorios

#### Asignaciones
- Hospital-Especialidad: ~25 asignaciones
- Especialidad-Consultorio: ~30 asignaciones
- Citas de ejemplo: 5 (distribuidas entre hospitales)

## 🔄 Nuevo Flujo de Reserva

### Paso a Paso

```mermaid
graph TD
    A[Paciente autenticado] --> B[GET /hospitals]
    B --> C[Selecciona Hospital]
    C --> D[GET /hospitals/{id}/specialties]
    D --> E[Selecciona Especialidad]
    E --> F[GET /slots/available?hospital_id=X&specialty_id=Y]
    F --> G[Selecciona Horario y Consultorio]
    G --> H[POST /appointments]
    H --> I[Cita Confirmada]
```

### Ejemplo Completo

#### 1. Listar Hospitales
```bash
GET /hospitals
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Hospital Nacional Rebagliati",
    "code": "HNR",
    "district": "Jesús María",
    "city": "Lima"
  },
  ...
]
```

#### 2. Ver Especialidades del Hospital
```bash
GET /hospitals/1/specialties
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 2,
    "name": "Cardiología",
    "description": "Especialista en enfermedades del corazón",
    "active": true,
    "available_rooms": 2  // Consultorios disponibles en este hospital
  },
  ...
]
```

#### 3. Ver Horarios Disponibles
```bash
GET /slots/available?hospital_id=1&specialty_id=2&date=2024-11-18&shift=morning
Authorization: Bearer <token>
```

**Response:**
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
    ...
  ]
}
```

#### 4. Reservar Cita
```bash
POST /appointments
Authorization: Bearer <token>
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

## 📦 Instrucciones de Implementación

### Opción 1: Base de Datos Nueva (Recomendado para desarrollo)

```bash
# 1. Eliminar base de datos existente
dropdb -U root neumoapp_db

# 2. Crear base de datos nueva
createdb -U root neumoapp_db

# 3. Crear esquema completo
psql -U root -d neumoapp_db -f scripts/database_schema.sql

# 4. Cargar datos de prueba
python init_db.py

# 5. Ejecutar aplicación
uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

### Opción 2: Migración de Base de Datos Existente

```bash
# 1. Hacer backup
pg_dump -U root neumoapp_db > backup_before_hospitals.sql

# 2. Ejecutar script de migración
psql -U root -d neumoapp_db -f migration_hospital_specialties.sql

# 3. Verificar
psql -U root -d neumoapp_db -c "SELECT * FROM v_hospitals_with_stats;"

# 4. Ejecutar aplicación
uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

## ✅ Verificación

### 1. Verificar Base de Datos

```sql
-- Ver hospitales
SELECT * FROM hospitals;

-- Ver asignaciones hospital-especialidad
SELECT * FROM v_hospital_specialties;

-- Ver consultorios con hospital
SELECT * FROM v_consultation_rooms_with_info;

-- Ver citas con hospital
SELECT * FROM v_upcoming_appointments;
```

### 2. Verificar API

```bash
# Listar hospitales
curl -H "Authorization: Bearer <token>" http://localhost:3000/hospitals

# Ver especialidades de un hospital
curl -H "Authorization: Bearer <token>" http://localhost:3000/hospitals/1/specialties

# Ver slots (debe incluir hospital_id)
curl -H "Authorization: Bearer <token>" \
  "http://localhost:3000/slots/available?hospital_id=1&specialty_id=2&date=2024-11-18&shift=morning"
```

### 3. Verificar Swagger UI

Ir a `http://localhost:3000/docs` y verificar:
- ✅ Endpoints de `/hospitals` disponibles
- ✅ Endpoint `/hospitals/{id}/specialties` funciona
- ✅ Endpoint `/slots/available` requiere `hospital_id`
- ✅ Modelos actualizados en la documentación

## 🎨 Beneficios de la Nueva Estructura

### 1. Realista
- Refleja estructura real de organizaciones de salud
- Hospitales pueden tener diferentes especialidades
- Facilita expansión a múltiples locaciones

### 2. Escalable
- Fácil agregar nuevos hospitales
- Reasignar especialidades entre hospitales
- Gestión independiente por hospital

### 3. Mejor UX
- Flujo intuitivo: Hospital → Especialidad → Horario
- Paciente sabe dónde irá antes de elegir especialidad
- Evita confusión al ver slots de múltiples hospitales

### 4. Administración
- Gestión centralizada de hospitales
- Asignación flexible de especialidades
- Estadísticas por hospital

## 📊 Comparación

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| **Hospitales** | ❌ No existía | ✅ Tabla completa |
| **Asignación Especialidades** | N/A | ✅ M:N con hospitales |
| **Consultorios** | Sin hospital | ✅ Pertenecen a hospital |
| **Flujo de Reserva** | Especialidad → Horario | ✅ Hospital → Especialidad → Horario |
| **Parámetros `/slots`** | `specialty_id, date, shift` | ✅ **`+ hospital_id`** |
| **Validaciones** | Básicas | ✅ Valida hospital ofrece especialidad |
| **Vistas BD** | 3 vistas | ✅ 5 vistas optimizadas |

## 🐛 Posibles Problemas y Soluciones

### Error: "No consultation rooms assigned to this specialty in the selected hospital"

**Causa:** El hospital no tiene consultorios asignados para esa especialidad.

**Solución:**
```sql
-- Verificar asignaciones
SELECT * FROM get_available_rooms_for_specialty(1, 2);

-- Asignar consultorio a especialidad
INSERT INTO specialty_consultation_rooms (specialty_id, consultation_room_id)
VALUES (2, 4);
```

### Error: "Hospital does not offer this specialty"

**Causa:** El hospital no tiene la especialidad en su oferta.

**Solución:**
```sql
-- Verificar especialidades del hospital
SELECT * FROM get_hospital_specialties(1);

-- Asignar especialidad a hospital
INSERT INTO hospital_specialties (hospital_id, specialty_id, active)
VALUES (1, 2, true);
```

### Error: Missing `hospital_id` parameter

**Causa:** Cliente intenta usar endpoint antiguo sin `hospital_id`.

**Solución:** Actualizar llamada a incluir `hospital_id`:
```bash
# ANTES
GET /slots/available?specialty_id=2&date=2024-11-18&shift=morning

# AHORA
GET /slots/available?hospital_id=1&specialty_id=2&date=2024-11-18&shift=morning
```

## 📝 Archivos Importantes

### Archivos Nuevos
- ✅ `app/models/hospital.py`
- ✅ `app/schemas/hospital.py`
- ✅ `app/repositories/hospital_repository.py`
- ✅ `app/services/hospital_service.py`
- ✅ `app/controllers/hospital_controller.py`
- ✅ `migration_hospital_specialties.sql`
- ✅ `CAMBIOS_HOSPITAL_SPECIALTIES.md` (este archivo)

### Archivos Modificados
- ✅ `app/models/specialty.py`
- ✅ `app/models/consultation_room.py`
- ✅ `app/models/__init__.py`
- ✅ `app/schemas/specialty.py`
- ✅ `app/schemas/consultation_room.py`
- ✅ `app/schemas/__init__.py`
- ✅ `app/repositories/consultation_room_repository.py`
- ✅ `app/services/hospital_service.py`
- ✅ `app/services/slot_service.py`
- ✅ `app/services/appointment_service.py`
- ✅ `app/controllers/hospital_controller.py`
- ✅ `app/controllers/slot_controller.py`
- ✅ `main.py`
- ✅ `init_db.py`
- ✅ `scripts/database_schema.sql`
- ✅ `README.md`

## 🎉 Resumen Final

Se ha implementado exitosamente un **sistema jerárquico de hospitales** que permite:

1. ✅ Gestionar múltiples hospitales
2. ✅ Asignar especialidades a hospitales
3. ✅ Vincular consultorios a hospitales
4. ✅ Flujo de reserva realista: Hospital → Especialidad → Turno
5. ✅ Validaciones robustas
6. ✅ Base de datos normalizada y eficiente
7. ✅ API RESTful completa y documentada
8. ✅ Datos de prueba para 3 hospitales

---

**Versión:** 4.0  
**Fecha:** Octubre 2024  
**Estado:** ✅ Completado e implementado

