#!/bin/bash

# ============================================================
# 🚀 IA Colombia Platform — Script de Inicialización
# ============================================================

set -e

echo ""
echo "🇨🇴 Iniciando configuración de IA Colombia Platform..."
echo ""

# ── 1. Estructura de carpetas ──────────────────────────────
echo "📁 Creando estructura de carpetas..."

mkdir -p ia-colombia-platform/{frontend,backend,ai-services,datasets/{raw,processed,notebooks},docs,docker}
cd ia-colombia-platform

echo "✅ Estructura creada"

# ── 2. Frontend (Next.js) ──────────────────────────────────
echo ""
echo "🖥️  Creando proyecto Next.js..."
cd frontend
npx create-next-app@latest . \
  --typescript \
  --eslint \
  --tailwind \
  --app \
  --src-dir \
  --import-alias "@/*" \
  --no-git \
  <<< $'\n\n\n\n\n\n\n'

npm install leaflet react-leaflet @types/leaflet recharts axios
echo "✅ Frontend listo"
cd ..

# ── 3. Backend (NestJS) ────────────────────────────────────
echo ""
echo "🔥 Creando proyecto NestJS..."
npm i -g @nestjs/cli --silent
nest new backend --package-manager npm --skip-git --language TS <<< $'\n'

cd backend
npm install prisma @prisma/client @nestjs/jwt @nestjs/passport passport passport-jwt bcrypt
npm install --save-dev @types/bcrypt @types/passport-jwt

# Inicializar Prisma
npx prisma init

# Crear módulos
nest g module auth --no-spec
nest g module users --no-spec
nest g module dashboard --no-spec
nest g module datasets --no-spec
nest g module predictions --no-spec
nest g module alerts --no-spec
nest g module maps --no-spec

echo "✅ Backend listo"
cd ..

# ── 4. AI Services (Python / FastAPI) ─────────────────────
echo ""
echo "🤖 Configurando AI Services..."
cd ai-services
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pandas scikit-learn python-dotenv --quiet
deactivate

echo "✅ AI Services listo"
cd ..

# ── 5. Levantar Docker ─────────────────────────────────────
echo ""
echo "🐳 Levantando Docker..."
docker compose up -d
echo "✅ PostgreSQL corriendo en puerto 5432"
echo "✅ PgAdmin en http://localhost:5050"

# ── 6. Done ────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════"
echo "🏆 ¡ia-colombia-platform listo!"
echo ""
echo "  Frontend:   cd frontend && npm run dev"
echo "  Backend:    cd backend  && npm run start:dev"
echo "  AI Service: cd ai-services && uvicorn main:app --reload"
echo "  PgAdmin:    http://localhost:5050  (admin@admin.com / admin)"
echo "════════════════════════════════════════════"
echo ""
