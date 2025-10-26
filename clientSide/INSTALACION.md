# 🚀 Guía de Instalación - Neumoapp Client

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Node.js** versión 18 o superior
- **npm** (incluido con Node.js) o **yarn**
- **Git** (opcional, para clonar el repositorio)
- **API de Neumoapp** corriendo en `http://localhost:3000`

Para verificar tus versiones:
```bash
node --version    # Debe ser v18.0.0 o superior
npm --version     # Cualquier versión reciente
```

## 📦 Paso 1: Instalar Dependencias

Desde el directorio del proyecto (`clientSide/`), ejecuta:

```bash
npm install
```

Esto instalará todas las dependencias necesarias:
- React 18
- React Router
- Axios
- Tailwind CSS
- Vite
- Y más...

### Solución de Problemas

Si encuentras errores durante la instalación:

**Error de permisos:**
```bash
sudo npm install
# o
npm install --unsafe-perm
```

**Cache corrupto:**
```bash
npm cache clean --force
npm install
```

**Dependencias desactualizadas:**
```bash
rm -rf node_modules package-lock.json
npm install
```

## ⚙️ Paso 2: Configurar Variables de Entorno

El proyecto necesita un archivo `.env` en la raíz del directorio `clientSide/`.

### Opción A: Usar el archivo de ejemplo

Si no existe el archivo `.env`, créalo copiando el ejemplo:

```bash
cp .env.example .env
```

### Opción B: Crear manualmente

Si `.env.example` está bloqueado, crea el archivo `.env` manualmente:

```bash
# En macOS/Linux
touch .env

# En Windows
type nul > .env
```

Y añade el siguiente contenido:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:3000
VITE_API_TIMEOUT=30000

# Application Configuration
VITE_APP_NAME=Neumoapp
VITE_APP_VERSION=1.0.0
```

### Personalización

Si tu API corre en otro puerto o dominio, modifica `VITE_API_BASE_URL`:

```env
# Para producción
VITE_API_BASE_URL=https://api.neumoapp.com

# Para otro puerto local
VITE_API_BASE_URL=http://localhost:8000
```

## 🚀 Paso 3: Iniciar el Servidor de Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en: **http://localhost:5173**

Deberías ver en la terminal:

```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### Opciones Adicionales

**Exponer a la red local:**
```bash
npm run dev -- --host
```

**Usar otro puerto:**
```bash
npm run dev -- --port 3001
```

## ✅ Paso 4: Verificar que Todo Funciona

1. Abre tu navegador en `http://localhost:5173`
2. Deberías ver la página de Login
3. Usa las credenciales de prueba:
   - **DNI:** `12345678`
   - **Password:** `password123`
4. Si el login funciona, verás el Dashboard

### Solución de Problemas Comunes

**Problema 1: Página en blanco**
- Abre la consola del navegador (F12)
- Verifica errores en la consola
- Asegúrate que la API esté corriendo

**Problema 2: Error de red al hacer login**
- Verifica que la API esté corriendo en `http://localhost:3000`
- Verifica `VITE_API_BASE_URL` en `.env`
- Verifica CORS en la API

**Problema 3: Error 401 Unauthorized**
- Verifica que las credenciales sean correctas
- Verifica que la base de datos tenga datos de prueba

## 🏗️ Paso 5: Build para Producción (Opcional)

Para crear una versión optimizada para producción:

```bash
npm run build
```

Esto generará los archivos en la carpeta `dist/`.

### Preview del Build

Para probar el build localmente:

```bash
npm run preview
```

La aplicación estará en `http://localhost:4173`

## 🔧 Scripts Disponibles

```bash
# Desarrollo
npm run dev          # Inicia servidor de desarrollo

# Build
npm run build        # Crea build de producción
npm run preview      # Preview del build

# Linting
npm run lint         # Ejecuta ESLint
```

## 📁 Verificar la Estructura

Después de la instalación, tu estructura debería verse así:

```
clientSide/
├── node_modules/        ✅ Creado después de npm install
├── dist/                ✅ Creado después de npm run build
├── src/
├── .env                 ✅ Debes crearlo
├── package.json
└── ...
```

## 🌐 Conectar con la API Backend

### Requisitos

1. La API debe estar corriendo
2. La API debe tener CORS habilitado para `http://localhost:5173`
3. La base de datos debe tener datos de prueba

### Verificar conexión

Puedes probar la API directamente:

```bash
# Test de health check (si existe)
curl http://localhost:3000/

# Test de login
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "document_number": "12345678",
    "password": "password123"
  }'
```

Si recibes un token JWT, la API está funcionando correctamente.

## 🔍 Herramientas de Desarrollo

### React DevTools
Instala la extensión React DevTools para tu navegador:
- [Chrome](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)
- [Firefox](https://addons.mozilla.org/en-US/firefox/addon/react-devtools/)

### Vite DevTools
El servidor de desarrollo de Vite incluye:
- Hot Module Replacement (HMR)
- Error overlay
- Source maps

## 📊 Monitoreo

### Ver logs de Vite
Los logs del servidor de desarrollo aparecen en la terminal donde ejecutaste `npm run dev`.

### Ver logs del navegador
Abre las DevTools del navegador (F12) para ver:
- Errores de JavaScript
- Llamadas a la API
- Estado de React

## 🐛 Debugging

### Habilitar source maps
Las source maps están habilitadas por defecto en desarrollo.

### Usar debugger
Puedes usar `debugger` en tu código:

```javascript
function handleLogin() {
  debugger; // El navegador pausará aquí
  // ... resto del código
}
```

## 🔄 Actualizar Dependencias

Para actualizar a las últimas versiones:

```bash
# Ver dependencias desactualizadas
npm outdated

# Actualizar dependencias menores
npm update

# Actualizar dependencias mayores (cuidado!)
npm install <package>@latest
```

## 🆘 Soporte

Si encuentras problemas:

1. Revisa esta guía completa
2. Verifica los logs de la terminal y navegador
3. Asegúrate que la API esté funcionando
4. Verifica las variables de entorno
5. Intenta reinstalar dependencias:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

## ✨ Próximos Pasos

Una vez que todo esté funcionando:

1. Explora la aplicación
2. Revisa el código en `src/`
3. Lee la documentación en `README.md`
4. Revisa la estructura en `ESTRUCTURA.md`
5. Comienza a desarrollar nuevas features

## 📚 Recursos Adicionales

- [Documentación de Vite](https://vitejs.dev/)
- [Documentación de React](https://react.dev/)
- [Documentación de Tailwind CSS](https://tailwindcss.com/)
- [Documentación de React Router](https://reactrouter.com/)

---

¡Feliz desarrollo! 🚀

