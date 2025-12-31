#!/bin/bash
# =====================================================
# Supabase Setup Script
# =====================================================
# Este script configura completamente Supabase para
# el sistema de onboarding de 48 preguntas
# =====================================================

set -e  # Exit on error

echo "🚀 Configurando Supabase para sistema de 48 preguntas..."
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# =====================================================
# 1. Verificar variables de entorno
# =====================================================

echo "📋 Paso 1: Verificando configuración..."

if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
    echo "Creando desde .env.example..."
    
    if [ -f ".env.example" ]; then
        cp .env.example backend/.env
        echo -e "${GREEN}✓${NC} Creado backend/.env desde .env.example"
        echo ""
        echo -e "${RED}❗ IMPORTANTE: Edita backend/.env con tus credenciales reales${NC}"
        echo ""
        echo "Necesitas configurar:"
        echo "  - SUPABASE_URL"
        echo "  - SUPABASE_SERVICE_KEY"
        echo "  - OPENAI_API_KEY"
        echo ""
        read -p "Presiona Enter cuando hayas configurado el archivo .env..."
    else
        echo -e "${RED}❌ No se encontró .env.example${NC}"
        exit 1
    fi
fi

# Cargar variables de entorno
if [ -f "backend/.env" ]; then
    export $(cat backend/.env | grep -v '^#' | xargs)
fi

# Verificar variables críticas
if [ -z "$SUPABASE_URL" ] || [ "$SUPABASE_URL" = "https://your-project.supabase.co" ]; then
    echo -e "${RED}❌ SUPABASE_URL no configurado en backend/.env${NC}"
    exit 1
fi

if [ -z "$SUPABASE_SERVICE_KEY" ] || [ "$SUPABASE_SERVICE_KEY" = "your-service-key-here" ]; then
    echo -e "${RED}❌ SUPABASE_SERVICE_KEY no configurado en backend/.env${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Variables de entorno configuradas"
echo ""

# =====================================================
# 2. Verificar conexión a Supabase
# =====================================================

echo "📡 Paso 2: Verificando conexión a Supabase..."

# Extraer project ref de URL
PROJECT_REF=$(echo $SUPABASE_URL | sed -n 's/.*https:\/\/\([^.]*\).*/\1/p')

if [ -z "$PROJECT_REF" ]; then
    echo -e "${RED}❌ No se pudo extraer project ref de SUPABASE_URL${NC}"
    exit 1
fi

echo "Project: $PROJECT_REF"

# Test API connection
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  "$SUPABASE_URL/rest/v1/" \
  -H "apikey: $SUPABASE_SERVICE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_KEY")

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✓${NC} Conexión exitosa a Supabase"
else
    echo -e "${RED}❌ Error conectando a Supabase (HTTP $HTTP_STATUS)${NC}"
    echo "Verifica tus credenciales en backend/.env"
    exit 1
fi

echo ""

# =====================================================
# 3. Ofrecer ejecutar migrations
# =====================================================

echo "🗄️  Paso 3: Migraciones de Base de Datos"
echo ""
echo "Se encontraron las siguientes migraciones:"
echo "  1. 001_initial_schema.sql - Schema base"
echo "  2. 002_add_48_questions.sql - Sistema de 48 preguntas"
echo ""

read -p "¿Quieres ejecutar las migraciones ahora? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo ""
    echo "🚀 Ejecutando migraciones vía Supabase API..."
    echo ""
    
    # Check if supabase CLI is installed
    if command -v supabase &> /dev/null; then
        echo "Usando Supabase CLI..."
        cd database/migrations
        
        # Run migrations
        for migration in *.sql; do
            echo "Ejecutando: $migration"
            supabase db execute --file "$migration" || {
                echo -e "${YELLOW}⚠️  Si falla, puedes ejecutar manualmente en Supabase Dashboard > SQL Editor${NC}"
            }
        done
        
        cd ../..
        echo -e "${GREEN}✓${NC} Migraciones ejecutadas"
    else
        echo -e "${YELLOW}ℹ️  Supabase CLI no instalado${NC}"
        echo ""
        echo "Opciones para ejecutar las migraciones:"
        echo ""
        echo "OPCIÓN 1: Supabase Dashboard (Recomendado)"
        echo "  1. Ve a: $SUPABASE_URL"
        echo "  2. Navega a: SQL Editor"
        echo "  3. Copia y pega el contenido de:"
        echo "     - database/migrations/001_initial_schema.sql"
        echo "     - database/migrations/002_add_48_questions.sql"
        echo "  4. Ejecuta cada script"
        echo ""
        echo "OPCIÓN 2: Instalar Supabase CLI"
        echo "  brew install supabase/tap/supabase"
        echo "  Luego vuelve a ejecutar este script"
        echo ""
        read -p "Presiona Enter cuando hayas ejecutado las migraciones..."
    fi
else
    echo ""
    echo -e "${YELLOW}⏭️  Saltando migraciones${NC}"
    echo ""
    echo "Puedes ejecutarlas manualmente después en:"
    echo "  Supabase Dashboard → SQL Editor"
    echo ""
fi

# =====================================================
# 4. Crear tenant de prueba
# =====================================================

echo ""
echo "👥 Paso 4: Configuración de Tenant"
echo ""

read -p "¿Crear tenant de prueba? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    TENANT_NAME="Test Healthcare Agency"
    
    echo "Creando tenant: $TENANT_NAME..."
    
    # Create tenant via API
    TENANT_RESPONSE=$(curl -s -X POST \
      "$SUPABASE_URL/rest/v1/tenants" \
      -H "apikey: $SUPABASE_SERVICE_KEY" \
      -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
      -H "Content-Type: application/json" \
      -H "Prefer: return=representation" \
      -d "{\"name\": \"$TENANT_NAME\"}")
    
    TENANT_ID=$(echo $TENANT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)[0]['id'])" 2>/dev/null || echo "")
    
    if [ ! -z "$TENANT_ID" ]; then
        echo -e "${GREEN}✓${NC} Tenant creado: $TENANT_ID"
        echo ""
        echo "Guarda este ID para usarlo en tus requests:"
        echo "  TENANT_ID=$TENANT_ID"
        echo ""
        
        # Save to .env if not already there
        if ! grep -q "TEST_TENANT_ID" backend/.env; then
            echo "" >> backend/.env
            echo "# Test Tenant" >> backend/.env
            echo "TEST_TENANT_ID=$TENANT_ID" >> backend/.env
            echo -e "${GREEN}✓${NC} Agregado a backend/.env"
        fi
    else
        echo -e "${YELLOW}⚠️  No se pudo crear tenant (puede que la tabla no exista aún)${NC}"
        echo "Ejecuta las migraciones primero"
    fi
fi

echo ""

# =====================================================
# 5. Verificar estructura de tablas
# =====================================================

echo "🔍 Paso 5: Verificando estructura de base de datos..."
echo ""

# Check if tables exist
TABLES_CHECK=$(curl -s "$SUPABASE_URL/rest/v1/clients?limit=0" \
  -H "apikey: $SUPABASE_SERVICE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
  -o /dev/null -w "%{http_code}")

if [ "$TABLES_CHECK" = "200" ]; then
    echo -e "${GREEN}✓${NC} Tabla 'clients' existe"
    
    # Check for new columns
    CLIENT_STRUCTURE=$(curl -s "$SUPABASE_URL/rest/v1/clients?limit=1" \
      -H "apikey: $SUPABASE_SERVICE_KEY" \
      -H "Authorization: Bearer $SUPABASE_SERVICE_KEY")
    
    if echo "$CLIENT_STRUCTURE" | grep -q "quick_start_data"; then
        echo -e "${GREEN}✓${NC} Columnas de 48 preguntas presentes"
    else
        echo -e "${YELLOW}⚠️  Columnas de 48 preguntas NO encontradas${NC}"
        echo "    Necesitas ejecutar: 002_add_48_questions.sql"
    fi
else
    echo -e "${YELLOW}⚠️  Tabla 'clients' no encontrada${NC}"
    echo "    Necesitas ejecutar: 001_initial_schema.sql"
fi

# Check conversation_sessions
SESSIONS_CHECK=$(curl -s "$SUPABASE_URL/rest/v1/conversation_sessions?limit=0" \
  -H "apikey: $SUPABASE_SERVICE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
  -o /dev/null -w "%{http_code}")

if [ "$SESSIONS_CHECK" = "200" ]; then
    echo -e "${GREEN}✓${NC} Tabla 'conversation_sessions' existe"
else
    echo -e "${YELLOW}⚠️  Tabla 'conversation_sessions' no encontrada${NC}"
    echo "    Necesitas ejecutar: 002_add_48_questions.sql"
fi

echo ""

# =====================================================
# 6. Resumen
# =====================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 RESUMEN DE CONFIGURACIÓN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Supabase URL: $SUPABASE_URL"
echo "Project: $PROJECT_REF"
echo ""

if [ ! -z "$TENANT_ID" ]; then
    echo "Tenant de prueba: $TENANT_ID"
    echo ""
fi

echo "Próximos pasos:"
echo ""
echo "1. Verifica que las migraciones se ejecutaron correctamente"
echo "   Dashboard: $SUPABASE_URL/project/$PROJECT_REF/editor"
echo ""
echo "2. Inicia el backend:"
echo "   cd backend"
echo "   uvicorn app.main:app --reload"
echo ""
echo "3. Prueba el endpoint de onboarding:"
echo "   curl -X POST http://localhost:8000/api/onboarding/start \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"tenant_id\": \"$TENANT_ID\", \"practice_name\": \"Test\"}'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ Setup de Supabase completado!${NC}"
echo ""
