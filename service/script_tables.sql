create table if not exists patients
(
    id              serial,
    document_number varchar(20)  not null,
    last_name       varchar(100) not null,
    first_name      varchar(100) not null,
    birth_date      date         not null,
    gender          varchar(1)   not null,
    address         text,
    phone           varchar(20),
    email           varchar(100) not null,
    password_hash   varchar(255) not null,
    active          boolean   default true,
    created_at      timestamp default CURRENT_TIMESTAMP,
    updated_at      timestamp default CURRENT_TIMESTAMP,
    primary key (id),
    unique (document_number),
    unique (email),
    constraint patients_gender_check
        check ((gender)::text = ANY ((ARRAY ['M'::character varying, 'F'::character varying])::text[]))
);

comment on table patients is 'Pacientes del sistema';

comment on column patients.document_number is 'DNI o documento de identidad';

comment on column patients.password_hash is 'Hash bcrypt de la contraseña';

create index if not exists idx_patients_document
    on patients (document_number);

create index if not exists idx_patients_email
    on patients (email);

create index if not exists idx_patients_active
    on patients (active);

create trigger update_patients_updated_at
    before update
    on patients
    for each row
execute procedure update_updated_at_column();

create table if not exists specialties
(
    id          serial,
    name        varchar(100) not null,
    description text,
    active      boolean   default true,
    created_at  timestamp default CURRENT_TIMESTAMP,
    updated_at  timestamp default CURRENT_TIMESTAMP,
    primary key (id),
    unique (name)
);

comment on table specialties is 'Especialidades médicas disponibles';

create index if not exists idx_specialties_active
    on specialties (active);

create index if not exists idx_specialties_name
    on specialties (name);

create trigger update_specialties_updated_at
    before update
    on specialties
    for each row
execute procedure update_updated_at_column();

create table if not exists hospitals
(
    id          serial,
    name        varchar(200) not null,
    code        varchar(20)  not null,
    address     text         not null,
    district    varchar(100),
    city        varchar(100) default 'Lima'::character varying,
    phone       varchar(20),
    email       varchar(100),
    description text,
    active      boolean      default true,
    created_at  timestamp    default CURRENT_TIMESTAMP,
    updated_at  timestamp    default CURRENT_TIMESTAMP,
    primary key (id),
    unique (code)
);

comment on table hospitals is 'Hospitales/clínicas donde se brindan servicios';

comment on column hospitals.code is 'Código único del hospital (ej: HNR, HAL)';

create index if not exists idx_hospitals_code
    on hospitals (code);

create index if not exists idx_hospitals_active
    on hospitals (active);

create index if not exists idx_hospitals_city
    on hospitals (city);

create trigger update_hospitals_updated_at
    before update
    on hospitals
    for each row
execute procedure update_updated_at_column();

create table if not exists hospital_specialties
(
    hospital_id  integer not null,
    specialty_id integer not null,
    active       boolean   default true,
    created_at   timestamp default CURRENT_TIMESTAMP,
    primary key (hospital_id, specialty_id),
    foreign key (hospital_id) references hospitals
        on delete cascade,
    foreign key (specialty_id) references specialties
        on delete cascade
);

comment on table hospital_specialties is 'Relación M:N entre hospitales y especialidades';

comment on column hospital_specialties.active is 'Permite desactivar temporalmente una especialidad en un hospital';

create index if not exists idx_hospital_specialties_hospital
    on hospital_specialties (hospital_id);

create index if not exists idx_hospital_specialties_specialty
    on hospital_specialties (specialty_id);

create table if not exists consultation_rooms
(
    id          serial,
    hospital_id integer      not null,
    room_number varchar(20)  not null,
    name        varchar(100) not null,
    floor       varchar(20),
    building    varchar(50),
    description varchar(255),
    active      boolean   default true,
    created_at  timestamp default CURRENT_TIMESTAMP,
    updated_at  timestamp default CURRENT_TIMESTAMP,
    primary key (id),
    unique (room_number),
    foreign key (hospital_id) references hospitals
        on delete restrict
);

comment on table consultation_rooms is 'Consultorios/salas de atención en hospitales';

comment on column consultation_rooms.hospital_id is 'Hospital al que pertenece el consultorio';

comment on column consultation_rooms.room_number is 'Código único del consultorio (ej: R-CARD-201)';

create index if not exists idx_consultation_rooms_hospital
    on consultation_rooms (hospital_id);

create index if not exists idx_consultation_rooms_room_number
    on consultation_rooms (room_number);

create index if not exists idx_consultation_rooms_active
    on consultation_rooms (active);

create trigger update_consultation_rooms_updated_at
    before update
    on consultation_rooms
    for each row
execute procedure update_updated_at_column();

create table if not exists specialty_consultation_rooms
(
    specialty_id         integer not null,
    consultation_room_id integer not null,
    created_at           timestamp default CURRENT_TIMESTAMP,
    primary key (specialty_id, consultation_room_id),
    foreign key (specialty_id) references specialties
        on delete cascade,
    foreign key (consultation_room_id) references consultation_rooms
        on delete cascade
);

comment on table specialty_consultation_rooms is 'Relación M:N entre especialidades y consultorios';

create index if not exists idx_specialty_rooms_specialty
    on specialty_consultation_rooms (specialty_id);

create index if not exists idx_specialty_rooms_room
    on specialty_consultation_rooms (consultation_room_id);

create table if not exists appointments
(
    id                   serial,
    patient_id           integer                                          not null,
    specialty_id         integer                                          not null,
    consultation_room_id integer                                          not null,
    appointment_date     date                                             not null,
    start_time           time                                             not null,
    end_time             time                                             not null,
    shift                varchar(20)                                      not null,
    status               varchar(20) default 'pending'::character varying not null,
    reason               text,
    observations         text,
    created_at           timestamp   default CURRENT_TIMESTAMP,
    updated_at           timestamp   default CURRENT_TIMESTAMP,
    primary key (id),
    foreign key (patient_id) references patients
        on delete cascade,
    foreign key (specialty_id) references specialties
        on delete restrict,
    foreign key (consultation_room_id) references consultation_rooms
        on delete restrict,
    constraint check_shift_valid
        check ((shift)::text = ANY ((ARRAY ['morning'::character varying, 'afternoon'::character varying])::text[])),
    constraint check_end_time_after_start_time
        check (end_time > start_time),
    constraint check_status_valid
        check ((status)::text = ANY
               ((ARRAY ['pending'::character varying, 'confirmed'::character varying, 'rescheduled'::character varying, 'cancelled'::character varying, 'completed'::character varying])::text[]))
);

comment on table appointments is 'Citas médicas agendadas';

comment on column appointments.start_time is 'Hora de inicio (slots de 20 minutos)';

comment on column appointments.end_time is 'Hora de fin (automático: start_time + 20 min)';

comment on column appointments.shift is 'Turno: morning (8-13h) o afternoon (14-18h)';

create index if not exists idx_appointments_patient
    on appointments (patient_id);

create index if not exists idx_appointments_specialty
    on appointments (specialty_id);

create index if not exists idx_appointments_consultation_room
    on appointments (consultation_room_id);

create index if not exists idx_appointments_date
    on appointments (appointment_date);

create index if not exists idx_appointments_status
    on appointments (status);

create index if not exists idx_appointments_specialty_date
    on appointments (specialty_id, appointment_date);

create index if not exists idx_appointments_room_date_time
    on appointments (consultation_room_id, appointment_date, start_time);

create trigger update_appointments_updated_at
    before update
    on appointments
    for each row
execute procedure update_updated_at_column();

