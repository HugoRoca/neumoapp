#!/usr/bin/env python3
"""Genera seed_patients_500_mysql.sql con ~500 pacientes de prueba.

El SQL generado son solo INSERT (sin SET de sesión): sirve en PostgreSQL y MySQL.
En MySQL, si hace falta: ejecutar antes `SET NAMES utf8mb4;` (opcional).

COUNT filas = COUNT usuarios. Los nombres se arman con 4 listas (primer/segundo × M/F) al azar;
la variedad es combinatoria. DNI y celular únicos; el email se deriva del nombre + apellidos y no se repite.
"""

import random
import unicodedata
from datetime import date, timedelta

OUT = "seed_patients_500_mysql.sql"
EMAIL_DOMAIN = "pnp.com.pe"
EMAIL_LOCAL_MAX = 64  # RFC práctico para la parte local
COUNT = 500
PASSWORD_HASH = "$2b$12$yBWexmtt1ya.iqhu2lPehOa4WaTQbDGdoOGd7l3M1jP14pKJqOZCW"  # bcrypt: password123

# Primer nombre (hombre)
HOMBRE_N1 = (
    "Juan", "José", "Luis", "Carlos", "Miguel", "Pedro", "Jorge", "Diego", "Roberto", "Andrés",
    "Daniel", "Francisco", "Manuel", "Ricardo", "Fernando", "Óscar", "César", "Edwin", "Marco", "Raúl",
    "Ángel", "Christian", "Bryan", "Julio", "Hugo", "Renzo", "Bruno", "Álvaro", "Gonzalo", "Rodrigo",
    "Felipe", "Jaime", "Alberto", "Víctor", "Eduardo", "Sergio", "Gustavo", "Arturo", "Héctor", "Wilfredo",
    "Elmer", "Moisés", "Samuel", "Nicolás", "Sebastián", "Matías", "Tomás", "Emilio", "Iván", "Pablo",
    "Roger", "Henry", "Kevin", "Anthony", "Franklin", "Jimmy", "Yuri", "Dante", "Joel", "Josué",
    "Efraín", "Isaac", "Abraham", "Jonás", "Elías", "Benjamín", "Adrián", "Cristian", "David", "Esteban",
    "Gabriel", "Hernán", "Julián", "Leonardo", "Martín", "Nelson", "Orlando", "Patricio", "Ramón", "Salvador",
    "Simón", "Ulises", "Valentín", "Walter", "Xavier", "Yonathan", "Jean", "Giancarlo", "Piero", "Mario",
)

# Segundo nombre (hombre)
HOMBRE_N2 = (
    "Carlos", "Luis", "Alberto", "Ángel", "Pablo", "Armando", "Felipe", "Alejandro", "Javier", "Antonio",
    "Andrés", "Raúl", "Augusto", "Martín", "Ernesto", "Gabriel", "Paul", "César", "Paolo", "Alessandro",
    "Iván", "Sebastián", "Eduardo", "Enrique", "Manuel", "Jesús", "Adolfo", "Gustavo", "David", "Isaac",
    "Esteban", "Ignacio", "Marcelo", "Junior", "Joel", "Alexander", "Miguel", "Alonso", "Daniel", "Moisés",
    "Elías", "Samuel", "Pedro", "Francisco", "José", "Fernando", "Rodrigo", "Emilio", "Rafael", "Tomás",
    "Santiago", "Enzo", "Dante", "Álvaro", "Óscar", "Hugo", "Renato", "Cristian", "Bryan", "Steve",
    "Pierre", "Alexis", "Maximiliano", "Gonzalo", "Víctor", "Ricardo", "Julio", "Vicente", "Fabián", "Mauricio",
    "Leandro", "Omar", "Rubén", "Sergio", "Tadeo", "Ulises", "Valentino", "Waldo", "Xavier", "Yago",
)

# Primer nombre (mujer)
MUJER_N1 = (
    "María", "Ana", "Rosa", "Carmen", "Patricia", "Lucía", "Gabriela", "Andrea", "Sandra", "Diana",
    "Karina", "Jessica", "Valeria", "Daniela", "Stephanie", "Fiorella", "Natalia", "Vanessa", "Melissa", "Ximena",
    "Luz", "Milagros", "Katherine", "Alexandra", "Brenda", "Cindy", "Doris", "Elizabeth", "Fabiola", "Gianella",
    "Haydee", "Ingrid", "Jasmin", "Karen", "Lissette", "Mónica", "Nancy", "Olga", "Pamela", "Lourdes",
    "Ruth", "Sofía", "Tatiana", "Verónica", "Wendy", "Yessenia", "Adriana", "Beatriz", "Claudia", "Delia",
    "Elena", "Flor", "Gloria", "Helen", "Iris", "Janet", "Katia", "Liliana", "Miriam", "Norma",
    "Ofelia", "Paola", "Susana", "Teresa", "Violeta", "Yolanda", "Zulema", "Alessandra", "Bianca", "Camila",
    "Danae", "Estefanía", "Fernanda", "Gisela", "Hilda", "Ivonne", "Jimena", "Kiara", "Lorena", "Marisol",
    "Nadia", "Olivia", "Priscila", "Romina", "Silvana", "Tania", "Úrsula", "Vanesa", "Wanda", "Yadira",
)

# Segundo nombre (mujer)
MUJER_N2 = (
    "Elena", "Lucía", "María", "Rosa", "Isabel", "Fernanda", "Alejandra", "Milagros", "Carolina", "Paola",
    "Nicole", "Rocío", "Andrea", "Angélica", "Lizeth", "Pilar", "Del Pilar", "Cecilia", "Teresa", "Luisa",
    "Victoria", "Esther", "Rita", "Carmen", "Jesús", "Auxiliadora", "Guadalupe", "Gracia", "Paz", "Soledad",
    "Consuelo", "Dolores", "Ángeles", "Fátima", "Valentina", "Camila", "Antonella", "Sofía", "Jimena", "Ariana",
    "Briana", "Daniela", "Fiorella", "Gianina", "Helena", "Ivana", "Jazmín", "Kiara", "Lía", "Mía",
    "Noelia", "Olga", "Priscila", "Regina", "Sabrina", "Tatiana", "Valeria", "Ximena", "Yamile", "Zoe",
    "Adriana", "Beatriz", "Claudia", "Diana", "Elisa", "Flavia", "Gloria", "Haydee", "Inés", "Josefina",
    "Karina", "Laura", "Mónica", "Natalia", "Pamela", "Ruth", "Silvia", "Tamara", "Vanessa", "Yolanda",
)


def nombre_compuesto(rng: random.Random, n1: tuple[str, ...], n2: tuple[str, ...]) -> str:
    """Une primer y segundo nombre; evita duplicar el mismo token (p. ej. José José)."""
    for _ in range(30):
        a, b = rng.choice(n1), rng.choice(n2)
        if a.casefold() != b.casefold():
            return f"{a} {b}"
    return f"{rng.choice(n1)} {rng.choice(n2)}"

APELLIDOS_P = (
    "García", "Rodríguez", "González", "López", "Martínez", "Sánchez", "Pérez", "Flores",
    "Vargas", "Castro", "Herrera", "Ruiz", "Ramos", "Mendoza", "Rojas", "Torres",
    "Díaz", "Salazar", "Reyes", "Morales", "Vega", "Cruz", "Silva", "Medina",
)

APELLIDOS_M = (
    "Quispe", "Huamán", "Ccahuana", "Yupanqui", "Távara", "Condori", "Mamani", "Apaza",
    "Chávez", "Espinoza", "Fernández", "Rivera", "Cárdenas", "Valdivia", "Paredes", "Núñez",
    "Palacios", "Sotomayor", "Villanueva", "Coronado", "Aguilar", "Bardales", "Córdova", "Delgado",
)

TIPO_VIA = ("Av.", "Jr.", "Calle")

# Nombres de vía (ejemplos tipo: Av. Los Olivos 234, Calle San Martín 890)
CALLES = (
    "Los Olivos",
    "San Martín",
    "Test",
    "Larco",
    "Brasil",
    "Arequipa",
    "Tacna",
    "México",
    "Venezuela",
    "Petit Thouars",
    "Angamos",
    "Inclán",
    "Paruro",
    "Huancavelica",
    "Cuzco",
    "Ayacucho",
    "García y García",
    "Salaverry",
    "Sucre",
    "La Marina",
    "El Polo",
    "Camino Real",
    "Alameda del Corregidor",
    "Prolongación Javier Prado",
)


def direccion_aleatoria(rng: random.Random) -> str:
    """Formato: Av.|Jr.|Calle + nombre + número + ', Lima'."""
    tipo = rng.choice(TIPO_VIA)
    calle = rng.choice(CALLES)
    num = rng.randint(100, 9999)
    return f"{tipo} {calle} {num}, Lima"


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "''")


def slugify_token(tok: str) -> str:
    """Token a fragmento ASCII para email (sin acentos, ñ→n)."""
    t = unicodedata.normalize("NFD", tok)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = t.translate(str.maketrans("ñÑ", "nn"))
    t = t.lower()
    return "".join(c for c in t if c.isascii() and c.isalnum())


def local_part_email(first_name: str, last_name: str) -> str:
    """p.ej. Juan Carlos + García Delgado → juan.carlos.garcia.delgado"""
    parts: list[str] = []
    for raw in (*first_name.split(), *last_name.split()):
        s = slugify_token(raw)
        if s:
            parts.append(s)
    base = ".".join(parts) if parts else "usuario"
    while ".." in base:
        base = base.replace("..", ".")
    base = base.strip(".") or "usuario"
    if len(base) > EMAIL_LOCAL_MAX:
        base = base[:EMAIL_LOCAL_MAX].rstrip(".")
    return base


def email_unico(used_locals: set[str], first_name: str, last_name: str, dni: str) -> str:
    """Email desde nombre+apellido; si colisiona, añade .2, .3, … o .{dni} como último recurso."""
    base = local_part_email(first_name, last_name)
    cand = base
    n = 2
    while cand in used_locals:
        suf = str(n)
        if n > 900:
            suf = dni
        room = EMAIL_LOCAL_MAX - len(suf) - 1
        prefix = base[: max(1, room)].rstrip(".")
        cand = f"{prefix}.{suf}"
        n += 1
    used_locals.add(cand)
    return f"{cand}@{EMAIL_DOMAIN}"


def main() -> None:
    rng = random.Random(42)
    start = date(1955, 1, 1)
    end = date(2005, 12, 31)
    span = (end - start).days

    lines = [
        f"-- Datos de prueba: {COUNT} filas INSERT (pacientes; dos nombres y dos apellidos).",
        "-- Celular: 9 dígitos (PE). password_hash = bcrypt de 'password123'.",
        "-- PostgreSQL / MySQL: sin SET de sesión (evita errores en PG).",
        "-- MySQL opcional antes de importar: SET NAMES utf8mb4;",
        "",
    ]

    rows = []
    used_docs: set[str] = set()
    used_phones: set[str] = set()
    used_email_locals: set[str] = set()

    for i in range(COUNT):
        gender = "M" if i % 2 == 0 else "F"
        if gender == "M":
            fn = nombre_compuesto(rng, HOMBRE_N1, HOMBRE_N2)
        else:
            fn = nombre_compuesto(rng, MUJER_N1, MUJER_N2)

        ln = f"{rng.choice(APELLIDOS_P)} {rng.choice(APELLIDOS_M)}"

        # DNI: 8 dígitos únicos
        while True:
            dni = f"{rng.randint(10_000_000, 99_999_999)}"
            if dni not in used_docs:
                used_docs.add(dni)
                break

        # Celular PE: 9 dígitos, empieza en 9
        while True:
            phone = "9" + "".join(str(rng.randint(0, 9)) for _ in range(8))
            if phone not in used_phones:
                used_phones.add(phone)
                break

        bd = start + timedelta(days=rng.randint(0, span))
        addr = direccion_aleatoria(rng)
        email = email_unico(used_email_locals, fn, ln, dni)

        rows.append(
            "('{doc}', '{ln}', '{fn}', '{bd}', '{g}', '{addr}', '{ph}', '{em}', '{pw}', TRUE)".format(
                doc=esc(dni),
                ln=esc(ln),
                fn=esc(fn),
                bd=bd.isoformat(),
                g=gender,
                addr=esc(addr),
                ph=esc(phone),
                em=esc(email),
                pw=esc(PASSWORD_HASH),
            )
        )

    assert len(rows) == COUNT, "debe haber exactamente COUNT filas"

    chunk = 100
    for c in range(0, len(rows), chunk):
        part = rows[c : c + chunk]
        lines.append(
            "INSERT INTO patients (document_number, last_name, first_name, birth_date, gender, address, phone, email, password_hash, active) VALUES\n"
            + ",\n".join(part)
            + ";"
        )
        lines.append("")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Written {OUT} ({COUNT} rows)")


if __name__ == "__main__":
    main()
