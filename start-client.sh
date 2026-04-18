#!/usr/bin/env bash
# Levanta el cliente Vite (React) desde clientSide/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT/clientSide"

if [[ ! -d node_modules ]]; then
  echo "📚 Instalando dependencias npm..."
  npm install
fi

echo ""
echo "🌐 Cliente: http://localhost:5173 (Vite)"
echo "   Asegúrate de que la API esté en el puerto que uses en .env (por defecto 3000)."
echo "   (Ctrl+C para detener)"
echo ""

exec npm run dev
