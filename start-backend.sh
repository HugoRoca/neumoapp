#!/usr/bin/env bash
# Levanta la API FastAPI (Neumoapp) desde service/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT/service"

# PostgreSQL (mismo compose que el README del servicio)
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  echo "📦 Iniciando PostgreSQL..."
  if docker compose version >/dev/null 2>&1; then
    docker compose up -d postgres
  else
    docker-compose up -d postgres
  fi
  echo "⏳ Esperando a la base de datos..."
  sleep 3
else
  echo "⚠️  Docker no disponible: asegúrate de que PostgreSQL esté accesible (p. ej. ya corriendo)."
fi

if [[ -f "neumoapp/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source neumoapp/bin/activate
elif [[ -f "venv/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source venv/bin/activate
else
  echo "❌ No hay venv en service/. Crea uno, por ejemplo:" >&2
  echo "   cd service && python3 -m venv neumoapp && source neumoapp/bin/activate && pip install -r requirements.txt" >&2
  exit 1
fi

PORT="${PORT:-3000}"
echo ""
echo "🚀 API: http://localhost:${PORT}"
echo "📖 Docs: http://localhost:${PORT}/docs"
echo "   (Ctrl+C para detener)"
echo ""

exec uvicorn main:app --reload --host 0.0.0.0 --port "${PORT}"
