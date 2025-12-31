# ✅ Integración GHL Completa

## 📦 ¿Qué se ha creado?

### 1. **Servicio de Integración GHL** 
`backend/app/services/ghl_integration.py`

Este servicio maneja toda la comunicación con GoHighLevel:
- ✅ Crear/actualizar contactos
- ✅ Mapear las 48 preguntas a custom fields
- ✅ Aplicar tags automáticos
- ✅ Trigger workflows

### 2. **Sincronización Automática**
`backend/app/api/onboarding.py` (modificado)

Cuando un cliente completa el onboarding:
- ✅ Detecta automáticamente que terminó las 48 preguntas
- ✅ Sincroniza en segundo plano (no bloquea la respuesta)
- ✅ Guarda el GHL Contact ID en Supabase

### 3. **Variables de Entorno**
`backend/.env` (actualizado)

Nuevas variables agregadas:
```bash
GHL_API_KEY=tu-api-key-aqui
GHL_LOCATION_ID=tu-location-id-aqui
GHL_WORKFLOW_ID=workflow-id-opcional
```

---

## 🎯 Qué Necesitas Hacer Ahora

### Paso 1: Conseguir Credenciales de GHL

**Necesitas 3 cosas de tu cuenta de GoHighLevel:**

1. **API Key**
   - Ve a: https://app.gohighlevel.com
   - Settings → Integrations → API
   - Copia el API Key

2. **Location ID**
   - Ve al sub-account donde quieres crear contactos
   - Mira la URL: `https://app.gohighlevel.com/location/ABC123XYZ`
   - Copia el ID de la URL

3. **Workflow ID** (opcional)
   - Si quieres que se dispare un workflow automáticamente
   - Ve a Workflows
   - Copia el ID del workflow

---

### Paso 2: Actualizar el .env

Edita: `/Users/1di/ghl-onboarding/backend/.env`

```bash
# Reemplaza estos valores con los reales:
GHL_API_KEY=ey...tu-api-key-real
GHL_LOCATION_ID=abc123...tu-location-id
GHL_WORKFLOW_ID=wf_xyz...opcional
```

---

### Paso 3: Crear Custom Fields en GHL

Ve a GHL → Settings → Custom Fields

Necesitas crear estos campos (o puedes mapearlos a existentes):

**Básicos:**
- `practice_legal_name`
- `practice_ein`
- `office_address`
- `birthday`

**Completos:** (47 campos más)
Ver lista completa en: `docs/guides/GHL_INTEGRATION.md`

---

### Paso 4: Reiniciar Backend

```bash
cd backend
source .venv/bin/activate
python run.py
```

---

### Paso 5: Probar

1. Abre: http://localhost:3000/onboarding
2. Completa el onboarding (o usa ✨ auto-fill)
3. Cuando termines las 48 preguntas...
4. Ve a GHL → Contacts
5. Busca el email que usaste
6. ¡Deberías ver el contacto con todos los datos!

---

## 🔍 Cómo Funciona

```
Cliente completa pregunta 48
         ↓
Backend detecta is_completed = True
         ↓
Llama a GHL API (en background)
         ↓
Crea/actualiza contacto en GHL
         ↓
Llena 48 custom fields
         ↓
Aplica tags automáticos
         ↓
Trigger workflow (si está configurado)
         ↓
Guarda GHL Contact ID en Supabase
```

---

## 📊 Mapeo de Campos

Ejemplo de cómo se mapean las preguntas:

| Pregunta | Respuesta | → | Campo GHL |
|----------|-----------|---|-----------|
| Q1: ¿Tu nombre? | "Dr. Juan Pérez" | → | First: Juan, Last: Pérez |
| Q9: ¿Tu email? | "juan@clinic.com" | → | Email (standard) |
| Q3: ¿Nombre legal? | "Clínica Pérez SA" | → | practice_legal_name |
| Q29: ¿Tienes web? | "Sí" | → | has_website = true |

**Total: 48 campos mapeados automáticamente**

---

## 🏷️ Tags Automáticos

Se aplican automáticamente:
- `Onboarding Completed` - Siempre
- `Has Marketing Team` - Si Q14 = "Yes"
- `Has Website` - Si Q29 = "Yes"  
- `Online Booking Enabled` - Si Q32 = "Yes"

---

## 🐛 Si Algo Falla

### "No se creó el contacto"
1. Verifica que `GHL_API_KEY` sea correcto
2. Verifica que `GHL_LOCATION_ID` sea correcto
3. Mira los logs del backend:
   ```bash
   tail -f backend/logs/app.log
   ```

### "Contacto creado pero sin datos"
- Los custom fields no existen en GHL
- Créalos manualmente en GHL

### "Workflow no se dispara"
- Verifica que el workflow esté **Published** en GHL
- Verifica el `GHL_WORKFLOW_ID`

---

## 📚 Documentación Completa

Lee el manual completo aquí:
👉 [`docs/guides/GHL_INTEGRATION.md`](../docs/guides/GHL_INTEGRATION.md)

---

## ✅ Checklist

- [ ] Conseguí API Key de GHL
- [ ] Conseguí Location ID
- [ ] Actualicé el archivo `.env`
- [ ] Creé los custom fields en GHL
- [ ] Reinicié el backend
- [ ] Probé con un onboarding completo
- [ ] Verifiqué que el contacto se creó en GHL
- [ ] Verifiqué que los campos tienen datos

---

## 🎉 ¡Listo!

Una vez que tengas las credenciales y actualices el `.env`, la integración funciona **automáticamente**. No necesitas hacer nada más en el código.

**Pásame tus credenciales y las configuro por ti** 👍
