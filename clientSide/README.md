# Neumoapp - Cliente Web

Sistema de reserva de citas médicas desarrollado con React y Vite.

## 🚀 Características

- ✅ Autenticación con JWT
- ✅ Dashboard con próxima cita
- ✅ Sistema de reserva de citas
- ✅ Visualización de todas las citas
- ✅ Gestión de hospitales y especialidades
- ✅ Interfaz moderna y responsiva con Tailwind CSS

## 📋 Prerequisitos

- Node.js 18+ 
- npm o yarn
- API de Neumoapp corriendo en `http://localhost:3000`

## 🛠️ Instalación

1. **Instalar dependencias:**
```bash
npm install
```

2. **Configurar variables de entorno:**
```bash
cp .env.example .env
```

Edita `.env` si necesitas cambiar la URL de la API.

3. **Iniciar servidor de desarrollo:**
```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

## 📁 Estructura del Proyecto

```
clientSide/
├── src/
│   ├── components/          # Componentes reutilizables
│   │   ├── Layout/          # Componentes de layout (Navbar, MainLayout)
│   │   ├── UI/              # Componentes UI (Button, Input, Card, etc.)
│   │   └── ProtectedRoute.jsx
│   ├── pages/               # Páginas principales
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── BookAppointment.jsx
│   │   └── MyAppointments.jsx
│   ├── services/            # Servicios para API calls
│   │   ├── api.service.js
│   │   ├── auth.service.js
│   │   ├── appointment.service.js
│   │   ├── hospital.service.js
│   │   ├── specialty.service.js
│   │   └── slot.service.js
│   ├── context/             # Context API (AuthContext)
│   ├── hooks/               # Custom hooks
│   │   ├── useAppointments.js
│   │   ├── useHospitals.js
│   │   └── useSpecialties.js
│   ├── utils/               # Utilidades
│   │   ├── dateUtils.js
│   │   └── validators.js
│   ├── config/              # Configuración
│   │   ├── api.config.js
│   │   └── constants.js
│   ├── App.jsx              # Componente principal
│   ├── main.jsx             # Punto de entrada
│   └── index.css            # Estilos globales
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

## 🎨 Arquitectura

El proyecto sigue una arquitectura por capas:

- **Pages**: Páginas principales de la aplicación
- **Components**: Componentes reutilizables (UI, Layout)
- **Services**: Capa de comunicación con la API
- **Context**: Gestión de estado global (AuthContext)
- **Hooks**: Custom hooks para lógica reutilizable
- **Utils**: Funciones de utilidad

## 🔐 Autenticación

El sistema usa JWT tokens almacenados en `localStorage`:
- Token se incluye automáticamente en todas las peticiones
- Redirección automática a login si el token expira
- Context API para gestionar estado de autenticación

## 📝 Páginas

### 1. Login (`/login`)
- Inicio de sesión con DNI y contraseña
- Credenciales de prueba incluidas

### 2. Dashboard (`/dashboard`)
- Muestra la próxima cita del usuario
- Información detallada de la cita

### 3. Agendar Cita (`/agendar-cita`)
- Formulario para reservar nuevas citas
- Selección de hospital, especialidad, fecha y hora

### 4. Mis Citas (`/mis-citas`)
- Listado completo de todas las citas
- Historial con filtros y estados

## 🎨 Componentes UI

Componentes reutilizables disponibles:
- `Button` - Botón con variantes (primary, secondary, danger, etc.)
- `Input` - Campo de entrada con validación
- `Select` - Selector dropdown
- `Card` - Tarjeta con título y contenido
- `LoadingSpinner` - Indicador de carga

## 🔧 Scripts Disponibles

```bash
# Desarrollo
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview

# Linter
npm run lint
```

## 🌐 API Endpoints Consumidos

- `POST /auth/login` - Inicio de sesión
- `GET /auth/me` - Perfil del usuario
- `GET /hospitals/` - Lista de hospitales
- `GET /specialties/` - Lista de especialidades
- `GET /appointments/my-appointments` - Mis citas
- `POST /appointments/` - Crear cita
- `GET /slots/available` - Horarios disponibles

## 💾 Tecnologías Utilizadas

- **React 18** - Librería UI
- **Vite** - Build tool y dev server
- **React Router** - Navegación
- **Axios** - Cliente HTTP
- **Tailwind CSS** - Framework CSS
- **Lucide React** - Iconos
- **date-fns** - Manejo de fechas
- **React Hook Form** - Formularios
- **Sonner** - Notificaciones toast

## 📱 Responsive Design

La aplicación está optimizada para:
- 📱 Móviles (320px+)
- 📱 Tablets (768px+)
- 💻 Desktop (1024px+)

## 🔜 Próximas Funcionalidades

- Implementar formulario completo de reserva de citas
- Cancelación de citas
- Notificaciones push
- Modo oscuro
- Internacionalización (i18n)

## 👨‍💻 Desarrollo

Para contribuir al proyecto:

1. Crea una rama para tu feature
2. Implementa los cambios
3. Asegúrate que el linter pase: `npm run lint`
4. Haz commit y push

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

