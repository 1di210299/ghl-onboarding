# 📊 Análisis del Proyecto: Sistema de Onboarding

**Fecha**: 30 de diciembre de 2025  
**Estado General**: 35% Completo

---

## 🎯 RESUMEN EJECUTIVO

**Tu sistema actual**: 10 preguntas básicas  
**Tu objetivo**: 48 preguntas en 4 etapas (Quick Start, Identity, Digital, Strategy)

---

## ✅ QUÉ TIENES COMPLETO

### Backend (90%)
- ✅ FastAPI con endpoints `/start`, `/message`, `/status`
- ✅ LangGraph workflow funcionando
- ✅ OpenAI GPT-4o integrado
- ✅ Validaciones: email, teléfono, URL, colores

### Base de Datos (100%)
- ✅ Tabla `clients` con 10 campos
- ✅ Row-Level Security (RLS)
- ✅ Índices y triggers

### GoHighLevel (95%)
- ✅ n8n workflow completo
- ✅ OAuth2 configurado
- ✅ Mapeo de campos automático

---

## ❌ QUÉ TE FALTA

### 1. **Integrar 48 Preguntas Reales** (6h)
- ✅ **Ya creadas**: `backend/app/config/questions.json` con 48 preguntas
- ❌ Actualizar `workflow.py` para leer de JSON
- ❌ Implementar sistema de 4 etapas (Quick Start, Team & Tech, Identity & Brand, Digital & Growth)
- ❌ Implementar 9 preguntas condicionales (Q15→Q14, Q30→Q29, etc.)

### 2. **Interfaz de Chat** (8h)
- ❌ No existe página `/onboarding`
- ❌ No hay input de mensajes
- ❌ No hay barra de progreso con etapas
- Solo tienes dashboard administrativo

### 3. **Sistema Pausa/Resume** (6h)
- ❌ No hay links de continuación
- ❌ No hay guardado de sesiones en DB (solo memoria)
- ❌ No hay emails de resume

### 4. **Validaciones Avanzadas** (3h)
- ❌ Números (revenue, patient count)
- ❌ Fechas y rangos
- ❌ Lógica if-then (dependencias)

---

## 📋 TAREAS PRIORITARIAS

### MUST HAVE (23h)

**1. ✅ Definir 48 Preguntas** (COMPLETO)
```bash
# ✅ YA CREADO: backend/app/config/questions.json
# 48 preguntas en 4 etapas:
# - Stage 1: Quick Start (9 preguntas)
# - Stage 2: Team & Tech (7 preguntas)  
# - Stage 3: Identity & Brand (12 preguntas)
# - Stage 4: Digital & Growth (20 preguntas)
# Ver detalles en: QUESTIONS_SUMMARY.md
```

**2. Crear Chat Interface** (8h)
```bash
# Crear archivos:
frontend/app/onboarding/page.tsx
frontend/components/chat/chat-interface.tsx
frontend/components/chat/message-input.tsx
frontend/components/chat/message-bubble.tsx
frontend/components/chat/progress-stages.tsx
```
**2. Refactor Backend con Questions.json** (6h)
```python
# Actualizar: backend/app/services/workflow.py
# - Cargar preguntas desde JSON
# - Implementar navegación por etapas
# - Agregar lógica condicional (9 dependencias)
# - Actualizar validators para nuevos tipos
```

**3. Crear Chat Interface** (8h)
**4. Migrar Sesiones a DB** (5h)
```sql
-- Nueva tabla
CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY,
**5. Sistema de Etapas** (4h) clients(id),
    session_state JSONB,
    current_stage TEXT,
    current_question INTEGER,
    resume_token TEXT UNIQUE,
### SHOULD HAVE (11h)

**6. Pausa/Resume** (6h)

**4. Sistema de Etapas** (4h)
- Agregar `current_stage` al state
- Calcular progreso por etapa
- Actualizar workflow.py

**7. Validaciones Avanzadas** (3h)

**5. Pausa/Resume** (6h)
```python
**8. Auto-save** (2h)services/resume_service.py
# Endpoints: GET /resume/:token, POST /pause
# Frontend: app/onboarding/resume/[token]/page.tsx
```

**6. Validaciones Avanzadas** (3h)
- Números, fechas, listas
- Preguntas condicionales
| Fase | Horas | Días |
|------|-------|------|
| **Must Have** | 23h | 3 días |
| **Should Have** | 11h | 1.5 días |
| **Testing** | 4h | 0.5 días |
| **TOTAL** | **38h** | **5 días** |

## ⏱️ ESTIMACIÓN

| Fase | Horas | Días |
|------|-------|------|
### **Día 1-2: Backend (14h)**
1. ✅ ~~Crear questions.json~~ (COMPLETO)
2. Refactor workflow.py para leer de JSON (6h)
3. Implementar lógica condicional (9 dependencias)
4. Crear tabla conversation_sessions (4h)
5. Actualizar validadores para nuevos tipos (2h)
---

## 🚀 PLAN DE IMPLEMENTACIÓN

### **Día 1-2: Backend (12h)**
1. Crear questions.json con 48 preguntas
2. Refactor workflow.py para etapas
3. Agregar preguntas condicionales
4. Crear tabla conversation_sessions

### **Día 3-4: Frontend (12h)**
1. Página /onboarding
2. ChatInterface component
3. ProgressStages component
4. Integrar con API

### **Día 5: Polish (12h)**
1. Sistema pause/resume
2. Validaciones avanzadas
3. Testing completo

---

## 📝 ARCHIVOS A CREAR

```
backend/
├── app/
│   ├── config/
│   │   └── questions.json          ❌ CREAR
│   ├── services/
│   │   └── resume_service.py       ❌ CREAR
│   └── api/
│       └── onboarding.py           ⚠️ EXTENDER

frontend/
├── app/
│   └── onboarding/
│       ├── page.tsx                ❌ CREAR
│       └── resume/[token]/page.tsx ❌ CREAR
└── components/
    └── chat/
        ├── chat-interface.tsx      ❌ CREAR
        ├── message-input.tsx       ❌ CREAR
        ├── message-bubble.tsx      ❌ CREAR
        └── progress-stages.tsx     ❌ CREAR

database/
└── migrations/
    └── 002_add_sessions.sql        ❌ CREAR
```

---
## ⚠️ ANTES DE EMPEZAR

- [x] ~~Definir las 48 preguntas exactas~~ ✅ **COMPLETO**
- [x] ~~Documentar reglas condicionales~~ ✅ **9 dependencias mapeadas**
- [ ] Confirmar límite de custom fields en GHL (necesitas 48+ campos)
- [ ] Decidir servicio de email (SendGrid/AWS SES)
- [ ] Revisar campos sensibles (Q4: EIN debe ser encriptado)GHL
- [ ] Decidir servicio de email (SendGrid?)

## 🎯 SIGUIENTE PASO

✅ **COMPLETADO**: `questions.json` con 48 preguntas en 4 etapas

**Ahora continuar con**:
1. Refactor `backend/app/services/workflow.py` para leer de JSON
2. Implementar lógica de navegación por etapas
3. Agregar validadores para preguntas condicionales

¿Empezamos con el refactor del workflow?` con las 48 preguntas estructuradas en 4 etapas.

¿Quieres que genere ese archivo ahora?
