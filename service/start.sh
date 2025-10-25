#!/bin/bash

# Script de inicio rápido para Neumoapp API

echo "🚀 Iniciando Neumoapp API..."
echo ""

# Verificar si Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor inicia Docker."
    exit 1
fi

# Iniciar PostgreSQL
echo "📦 Iniciando PostgreSQL..."
docker-compose up -d postgres

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a que PostgreSQL esté listo..."
sleep 5

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "🔧 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔌 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -q -r requirements.txt

# Inicializar base de datos si es necesario
echo "🗄️  Verificando base de datos..."
python init_db.py

# Iniciar la API
echo ""
echo "✅ Todo listo! Iniciando la API..."
echo ""
echo "📍 La API estará disponible en: http://localhost:8000"
echo "📖 Documentación: http://localhost:8000/docs"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000

