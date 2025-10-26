# 📁 Estructura del Proyecto - Neumoapp Client

## Estructura Completa de Carpetas y Archivos

```
clientSide/
│
├── 📄 index.html                    # HTML principal
├── 📄 package.json                  # Dependencias y scripts
├── 📄 vite.config.js               # Configuración de Vite
├── 📄 tailwind.config.js           # Configuración de Tailwind CSS
├── 📄 postcss.config.js            # Configuración de PostCSS
├── 📄 eslint.config.js             # Configuración de ESLint
├── 📄 .gitignore                   # Archivos ignorados por Git
├── 📄 .cursorignore                # Archivos ignorados por Cursor
├── 📄 README.md                    # Documentación principal
├── 📄 ESTRUCTURA.md                # Este archivo
│
└── 📂 src/
    │
    ├── 📄 main.jsx                 # Punto de entrada de la aplicación
    ├── 📄 App.jsx                  # Componente raíz con rutas
    ├── 📄 index.css                # Estilos globales y Tailwind
    │
    ├── 📂 pages/                   # 🎯 Páginas principales
    │   ├── Login.jsx               # Página de inicio de sesión
    │   ├── Dashboard.jsx           # Dashboard con próxima cita
    │   ├── BookAppointment.jsx     # Formulario de reserva de cita
    │   └── MyAppointments.jsx      # Listado de todas las citas
    │
    ├── 📂 components/              # 🧩 Componentes reutilizables
    │   │
    │   ├── ProtectedRoute.jsx      # HOC para rutas protegidas
    │   │
    │   ├── 📂 Layout/              # Componentes de estructura
    │   │   ├── Navbar.jsx          # Barra de navegación
    │   │   └── MainLayout.jsx      # Layout principal con navbar
    │   │
    │   └── 📂 UI/                  # Componentes de interfaz
    │       ├── Button.jsx          # Botón reutilizable
    │       ├── Input.jsx           # Campo de entrada
    │       ├── Select.jsx          # Selector dropdown
    │       ├── Card.jsx            # Tarjeta contenedora
    │       └── LoadingSpinner.jsx  # Indicador de carga
    │
    ├── 📂 services/                # 🔌 Servicios de API
    │   ├── api.service.js          # Cliente Axios configurado
    │   ├── auth.service.js         # Autenticación
    │   ├── appointment.service.js  # Citas médicas
    │   ├── hospital.service.js     # Hospitales
    │   ├── specialty.service.js    # Especialidades médicas
    │   └── slot.service.js         # Horarios disponibles
    │
    ├── 📂 context/                 # 🌐 Context API
    │   └── AuthContext.jsx         # Context de autenticación
    │
    ├── 📂 hooks/                   # 🪝 Custom Hooks
    │   ├── useAppointments.js      # Hook para obtener citas
    │   ├── useHospitals.js         # Hook para obtener hospitales
    │   └── useSpecialties.js       # Hook para obtener especialidades
    │
    ├── 📂 utils/                   # 🛠️ Utilidades
    │   ├── dateUtils.js            # Funciones para fechas
    │   └── validators.js           # Validaciones de formularios
    │
    └── 📂 config/                  # ⚙️ Configuración
        ├── api.config.js           # Configuración de API y endpoints
        └── constants.js            # Constantes globales
```

## 📊 Descripción de Capas

### 1. 🎯 Pages (Páginas)
Componentes de nivel superior que representan rutas completas:
- **Login**: Autenticación de usuarios
- **Dashboard**: Vista principal con próxima cita
- **BookAppointment**: Formulario para agendar citas
- **MyAppointments**: Historial de citas

### 2. 🧩 Components (Componentes)
Componentes reutilizables organizados por función:

#### Layout
- Componentes de estructura y navegación
- MainLayout, Navbar

#### UI
- Componentes básicos de interfaz
- Button, Input, Select, Card, LoadingSpinner

### 3. 🔌 Services (Servicios)
Capa de comunicación con la API:
- Cada servicio maneja un dominio específico
- Cliente Axios centralizado con interceptores
- Manejo de tokens JWT automático

### 4. 🌐 Context
Estado global de la aplicación:
- **AuthContext**: Gestión de autenticación y usuario

### 5. 🪝 Hooks
Custom hooks para lógica reutilizable:
- Fetching de datos
- Lógica de negocio compartida

### 6. 🛠️ Utils
Funciones de utilidad:
- Formateo de fechas
- Validaciones
- Helpers varios

### 7. ⚙️ Config
Configuración centralizada:
- URLs de API
- Constantes de la aplicación
- Endpoints

## 🔄 Flujo de Datos

```
Usuario → Page → Hook → Service → API
                  ↓
                Context
                  ↓
              Components
```

## 🎨 Patrones de Diseño

### 1. Separation of Concerns
- Cada capa tiene una responsabilidad única
- Services solo hacen llamadas a API
- Components solo renderizan UI
- Hooks manejan lógica de estado

### 2. Component Composition
- Componentes pequeños y reutilizables
- Props para customización
- Children para flexibilidad

### 3. Custom Hooks
- Encapsulan lógica compleja
- Reutilizables entre componentes
- Facilitan testing

### 4. Context API
- Estado global sin prop drilling
- AuthContext para autenticación
- Fácil de extender

## 📦 Tecnologías por Capa

### Frontend Framework
- **React 18**: Librería UI
- **React Router**: Navegación

### Build & Dev
- **Vite**: Build tool rápido
- **ESLint**: Linter

### Styling
- **Tailwind CSS**: Framework CSS utility-first
- **PostCSS**: Procesador CSS

### HTTP & Data
- **Axios**: Cliente HTTP
- **Context API**: Estado global

### Utilities
- **date-fns**: Manejo de fechas
- **Lucide React**: Iconos
- **Sonner**: Notificaciones toast
- **React Hook Form**: Formularios
- **React Calendar**: Selector de fechas

## 🚀 Próximos Pasos

1. **Implementar BookAppointment completo**
   - Formulario multi-paso
   - Integración con calendario
   - Selección de horarios

2. **Agregar más funcionalidades**
   - Cancelación de citas
   - Edición de perfil
   - Notificaciones

3. **Mejorar UX**
   - Animaciones
   - Modo oscuro
   - Loading states

4. **Testing**
   - Unit tests
   - Integration tests
   - E2E tests

## 📝 Convenciones de Código

### Nombres de Archivos
- Componentes: `PascalCase.jsx`
- Hooks: `useCamelCase.js`
- Utils: `camelCase.js`
- Services: `camelCase.service.js`

### Imports
- Usar alias `@/` para imports absolutos
- Agrupar imports por tipo:
  1. React/Librerías
  2. Componentes
  3. Hooks
  4. Utils
  5. Tipos/Constantes

### Componentes
- Functional components con hooks
- Props destructuring
- PropTypes o TypeScript (futuro)

### Estilos
- Tailwind CSS classes
- Utility-first approach
- Custom classes en index.css cuando sea necesario

## 🔐 Seguridad

- Token JWT en localStorage
- Interceptores para refresh automático
- Validación client-side
- Rutas protegidas con ProtectedRoute

## 📱 Responsive

- Mobile-first approach
- Breakpoints de Tailwind:
  - sm: 640px
  - md: 768px
  - lg: 1024px
  - xl: 1280px
  - 2xl: 1536px

