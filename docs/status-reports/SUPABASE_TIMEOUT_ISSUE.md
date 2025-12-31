# PROBLEMA IDENTIFICADO

## Supabase Timeout

El proyecto de Supabase (`gbwrzkiegehmmdqfvojm`) está experimentando timeouts en todas las peticiones.

### Evidencia:
```bash
curl -X POST "https://gbwrzkiegehmmdqfvojm.supabase.co/rest/v1/clients" ...
# Result: curl: (28) Operation timed out after 30001 milliseconds
```

### Causa probable:
- **Proyecto pausado** (Supabase free tier pausa proyectos tras 7 días de inactividad)
- Problema de red con Supabase
- Proyecto eliminado

### Solución:
1. Ir a https://supabase.com/dashboard/project/gbwrzkiegehmmdqfvojm
2. Si está pausado, hacer clic en "Resume Project"
3. Esperar 1-2 minutos para que el proyecto despierte
4. Reintentar

### Alternativa temporal:
Usar modo de desarrollo sin Supabase (almacenamiento en memoria) modificando `backend/.env`:
```
USE_MEMORY_STORAGE=true
```

Esto permitirá probar el frontend mientras se resuelve el problema de Supabase.
