# 🚀 Inicio Rápido - Neumoapp Client

## ✅ Ya está todo configurado!

La estructura del proyecto React está **completamente lista**. Solo necesitas seguir 3 pasos simples para comenzar.

---

## 📝 Paso 1: Instalar Dependencias

Abre la terminal en la carpeta `clientSide/` y ejecuta:

```bash
npm install
```

⏱️ Esto tomará unos 2-3 minutos dependiendo de tu conexión.

---

## 🔧 Paso 2: Configurar Variables de Entorno

Crea un archivo llamado `.env` en la raíz del proyecto (junto a `package.json`):

### Opción A: Copiar desde plantilla (si existe)
```bash
cp .env.example .env
```

### Opción B: Copiar desde template
```bash
# macOS/Linux
cat env.template.txt > .env

# Windows
type env.template.txt > .env
```

### Opción C: Crear manualmente
Crea el archivo `.env` y copia este contenido:

```env
VITE_API_BASE_URL=http://localhost:3000
VITE_API_TIMEOUT=30000
VITE_APP_NAME=Neumoapp
VITE_APP_VERSION=1.0.0
```

---

## 🎯 Paso 3: Iniciar el Proyecto

```bash
npm run dev
```

🌐 Abre tu navegador en: **http://localhost:5173**

---

## 🎉 ¡Listo! Deberías ver la página de Login

### Credenciales de Prueba
- **DNI:** `12345678`
- **Password:** `password123`

---

## 📱 Páginas Disponibles

Una vez que inicies sesión, tendrás acceso a:

| Ruta | Página | Descripción |
|------|--------|-------------|
| `/login` | Login | Autenticación |
| `/dashboard` | Dashboard | Próxima cita |
| `/agendar-cita` | Agendar Cita | Reservar nueva cita |
| `/mis-citas` | Mis Citas | Historial de citas |

---

## 🛠️ Comandos Útiles

```bash
# Desarrollo
npm run dev              # Iniciar servidor (puerto 5173)

# Build
npm run build            # Crear versión de producción
npm run preview          # Previsualizar build

# Linting
npm run lint             # Ejecutar linter
```

---

## 📚 Documentación

| Archivo | ¿Cuándo leerlo? |
|---------|-----------------|
| `README.md` | Documentación completa |
| `INSTALACION.md` | Si tienes problemas instalando |
| `ESTRUCTURA.md` | Para entender la organización |
| `RESUMEN_CONFIGURACION.md` | Ver qué se implementó |

---

## ⚠️ Requisitos Previos

Asegúrate de tener:

- ✅ Node.js 18+ instalado
- ✅ API backend corriendo en `http://localhost:3000`
- ✅ Base de datos con datos de prueba

### Verificar Node.js
```bash
node --version   # Debe mostrar v18.0.0 o superior
```

### Verificar API
```bash
curl http://localhost:3000/
```

---

## 🐛 Solución de Problemas Rápida

### "No se encuentra npm"
Instala Node.js desde [nodejs.org](https://nodejs.org/)

### "Error al conectar con la API"
1. Verifica que la API esté corriendo en puerto 3000
2. Revisa el archivo `.env`
3. Verifica CORS en la API

### "Página en blanco"
1. Abre la consola del navegador (F12)
2. Busca errores en la pestaña Console
3. Verifica que completaste el Paso 2 (`.env`)

### "Error al hacer login"
1. Verifica las credenciales: `12345678` / `password123`
2. Asegúrate que la base de datos tenga datos de prueba
3. Verifica la URL de la API en `.env`

---

## 🎨 Lo que Ya Está Implementado

### ✅ Autenticación Completa
- Login con JWT
- Protección de rutas
- Logout automático

### ✅ Dashboard Funcional
- Muestra próxima cita
- Información detallada
- Estado de cita

### ✅ Historial de Citas
- Lista todas tus citas
- Filtra por estado
- Información completa

### ✅ Componentes Reutilizables
- Button, Input, Select
- Card, LoadingSpinner
- Navbar, Layout

### ✅ Servicios de API
- Autenticación
- Citas
- Hospitales
- Especialidades
- Horarios

---

## 🔜 Siguiente: Implementar Formulario de Reserva

La página "Agendar Cita" tiene la estructura base lista. El siguiente paso será implementar:

1. Selector de hospital
2. Selector de especialidad
3. Calendario de fechas
4. Selector de horarios
5. Formulario de reserva

**Pero eso es para después!** Por ahora, el proyecto está listo para explorar.

---

## 💡 Tips para Comenzar

1. **Explora el código** - Todo está bien organizado y comentado
2. **Usa los componentes** - Ya hay componentes reutilizables listos
3. **Aprovecha los hooks** - `useAppointments`, `useHospitals`, etc.
4. **Lee el código de ejemplo** - Dashboard y MyAppointments son buenos ejemplos

---

## 📊 Estadísticas del Proyecto

```
✅ 43 archivos creados
✅ 13 componentes React
✅ 6 servicios API
✅ 3 custom hooks
✅ 4 páginas
✅ 0 errores de linter
```

---

## 🎯 Arquitectura

```
Usuario
  ↓
Página (Login, Dashboard, etc.)
  ↓
Hook (useAppointments, etc.)
  ↓
Servicio (appointment.service.js)
  ↓
API Backend (http://localhost:3000)
```

---

## ✨ ¡Estás Listo!

```
┌─────────────────────────────────────┐
│                                     │
│   🎉 TODO ESTÁ CONFIGURADO 🎉      │
│                                     │
│   Ejecuta:  npm install             │
│   Después:  npm run dev             │
│   Abre:     http://localhost:5173   │
│                                     │
└─────────────────────────────────────┘
```

---

**¿Preguntas?** Revisa los otros archivos de documentación o explora el código. ¡Todo está comentado y organizado! 🚀

