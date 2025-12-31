# DigitalOcean Deployment Files

Este directorio contiene los archivos necesarios para desplegar en DigitalOcean App Platform.

## Archivos

- **`app.yaml`**: Especificación de la aplicación para DigitalOcean App Platform
- **`deploy.sh`**: Script automatizado para despliegue
- **`README.md`**: Este archivo

## Uso Rápido

```bash
# 1. Autenticar
doctl auth init --access-token YOUR_DIGITALOCEAN_TOKEN_HERE

# 2. Desplegar
chmod +x deploy.sh
./deploy.sh
```

## Comandos Útiles

```bash
# Listar apps
doctl apps list

# Ver detalles
doctl apps get <app-id>

# Ver logs
doctl apps logs <app-id> --type run --follow

# Forzar redespliegue
doctl apps create-deployment <app-id>

# Actualizar configuración
doctl apps update <app-id> --spec app.yaml
```

## Documentación Completa

Ver: `/DEPLOYMENT_DO.md` en la raíz del proyecto
