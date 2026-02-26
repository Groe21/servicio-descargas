# 🚂 Despliegue en Railway

## 🎯 Railway: Deploy en 5 minutos

Railway es una plataforma moderna que detecta y despliega automáticamente tu aplicación.

### ✅ Pre-requisitos
- Cuenta en [Railway.app](https://railway.app) (gratis)
- Código en GitHub (o deploy directo desde CLI)

---

## 🚀 Método 1: Deploy desde GitHub (Recomendado)

### Paso 1: Subir código a GitHub

```bash
cd "/home/emilio/Escritorio/desarrollador/servicio descargas"

# Inicializar repositorio git
git init

# Agregar archivos
git add .

# Commit inicial
git commit -m "YouTube MP3 Downloader - Railway ready"

# Crear repositorio en GitHub y conectar
git remote add origin https://github.com/TU-USUARIO/youtube-downloader.git
git branch -M main
git push -u origin main
```

### Paso 2: Conectar con Railway

1. Ve a [railway.app](https://railway.app)
2. Click en **"Start a New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Autoriza Railway en GitHub
5. Selecciona tu repositorio `youtube-downloader`
6. Railway detectará automáticamente que es una app Python

### Paso 3: Configurar Variables de Entorno

En Railway, ve a tu proyecto → **Variables**:

```
TEMP_DIR=/tmp/youtube_downloads
DEBUG=False
```

### Paso 4: ¡Deploy automático!

Railway desplegará automáticamente. Verás el proceso en tiempo real.

**URL de tu app:** `https://tu-proyecto.up.railway.app`

---

## 🚀 Método 2: Deploy con Railway CLI

### Instalar Railway CLI

```bash
# Instalar con npm
npm i -g @railway/cli

# O con homebrew (macOS)
brew install railway
```

### Deploy

```bash
cd "/home/emilio/Escritorio/desarrollador/servicio descargas"

# Login en Railway
railway login

# Inicializar proyecto
railway init

# Deploy
railway up
```

---

## 📋 Archivos Configurados para Railway

### ✅ Procfile
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT --timeout 120 app:app
```
Define cómo ejecutar la aplicación en producción.

### ✅ railway.json
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "gunicorn -w 4 -b 0.0.0.0:$PORT --timeout 120 app:app",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### ✅ requirements.txt
Todas las dependencias listadas correctamente.

### ✅ app.py
Puerto configurado desde variable de entorno `$PORT`.

---

## 🔧 Configuración Adicional en Railway

### Variables de Entorno Recomendadas

```bash
# Esenciales
PORT=5000                              # Auto-configurado por Railway
DEBUG=False                            # Desactivar debug en producción
TEMP_DIR=/tmp/youtube_downloads        # Directorio temporal

# Opcionales
MAX_DURATION=600                       # Máximo 10 minutos por video
RATE_LIMIT_REQUESTS=5                  # Descargas por hora
RATE_LIMIT_WINDOW=3600                 # Ventana de tiempo (segundos)
```

### Configurar en Railway:

1. Ve a tu proyecto
2. Click en **Variables**
3. Agrega cada variable
4. Railway redesplegará automáticamente

---

## 📊 Monitoreo en Railway

Railway proporciona:

- **Logs en tiempo real**: Ver errores y actividad
- **Métricas**: CPU, RAM, Red
- **Dominios**: Asignar dominio personalizado
- **Escalado**: Ajustar recursos según necesidad

### Ver Logs

```bash
# Con CLI
railway logs

# O en la web: Proyecto → Deployments → Click en deployment → Logs
```

---

## 🌐 Dominio Personalizado

### En Railway Dashboard:

1. Ve a **Settings**
2. Sección **Domains**
3. Click **Generate Domain** (dominio gratuito de Railway)
4. O agrega tu dominio personalizado

---

## ⚠️ Consideraciones Importantes

### 1. Almacenamiento Efímero

Railway usa almacenamiento efímero. Los archivos en `/tmp` se borran al reiniciar.

**✅ Nuestra app ya maneja esto correctamente:**
- Archivos temporales se eliminan inmediatamente
- No hay almacenamiento persistente necesario

### 2. FFmpeg en Railway

**✅ FFmpeg ya está incluido en Railway** por defecto con el builder NIXPACKS.

Si necesitas verificar o instalar manualmente, crea `nixpacks.toml`:

```toml
[phases.setup]
aptPkgs = ["ffmpeg"]
```

### 3. Timeouts

Railway tiene timeouts. Configuramos 120 segundos en Gunicorn, pero videos muy largos pueden fallar.

**Solución:** Mantener límite de 10 minutos (ya implementado).

### 4. Rate Limiting

Railway puede tener límites en el plan gratuito:
- 500 horas/mes de ejecución
- $5 de crédito gratis

Monitorea tu uso en el dashboard.

---

## 🆓 Planes de Railway

### Plan Gratuito (Hobby)
- $5 de crédito gratis/mes
- Sin tarjeta de crédito requerida
- Perfecto para pruebas y proyectos personales

### Plan Developer ($5/mes)
- $5 de crédito incluido
- Sin límites de builds
- Mejor para producción

---

## 🐛 Troubleshooting en Railway

### Build falla

**Verificar logs:**
```bash
railway logs --deployment
```

**Problema común:** Falta `requirements.txt`
**Solución:** Ya está incluido ✅

### App no inicia

**Verificar Procfile:**
```bash
cat Procfile
```

Debe contener:
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT --timeout 120 app:app
```

### Error 403 en descargas

**Causa:** YouTube bloquea Railway IPs a veces.

**Solución:** Usar cookies (ver [TROUBLESHOOTING.md](TROUBLESHOOTING.md))

### Descargas muy lentas

**Causa:** Recursos limitados en plan gratuito.

**Solución:** 
1. Reducir calidad a 128kbps en lugar de 192kbps
2. Actualizar a plan Developer

---

## 🔄 Actualizar Deploy

### Con GitHub (automático):

```bash
git add .
git commit -m "Update"
git push
```

Railway detecta el push y redespliega automáticamente.

### Con CLI:

```bash
railway up
```

---

## 📈 Optimizaciones para Producción

### 1. Aumentar Workers

En `Procfile`, ajusta según recursos:
```
web: gunicorn -w 2 -b 0.0.0.0:$PORT --timeout 120 app:app
```

**Recomendación Railway:** 2-4 workers

### 2. Agregar Health Checks

Railway puede monitorear `/api/health`:

En `railway.json`:
```json
{
  "deploy": {
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 10
  }
}
```

### 3. Configurar Reinicio Automático

Ya configurado en `railway.json` ✅:
```json
"restartPolicyType": "ON_FAILURE",
"restartPolicyMaxRetries": 10
```

---

## 🎯 Checklist de Deploy

- [x] Procfile creado
- [x] railway.json configurado
- [x] requirements.txt actualizado
- [x] Puerto dinámico ($PORT) configurado en app.py
- [x] .dockerignore agregado
- [x] .gitignore configurado
- [x] FFmpeg incluido (por defecto en Railway)
- [x] Limpieza automática de archivos implementada
- [ ] Código subido a GitHub
- [ ] Proyecto creado en Railway
- [ ] Variables de entorno configuradas
- [ ] Deploy exitoso

---

## 🚦 Quick Start

```bash
# 1. Subir a GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TU-USUARIO/youtube-downloader.git
git push -u origin main

# 2. Ir a railway.app
# 3. "New Project" → "Deploy from GitHub repo"
# 4. Seleccionar repositorio
# 5. ¡Listo! URL automática generada
```

---

## 📞 Soporte

- **Documentación Railway:** [docs.railway.app](https://docs.railway.app)
- **Discord Railway:** [railway.app/discord](https://railway.app/discord)
- **Status:** [railway.statuspage.io](https://railway.statuspage.io)

---

## 🎉 Deploy Completado

Tu app estará disponible en:
```
https://tu-proyecto-randomid.up.railway.app
```

**Funciones disponibles:**
- ✅ Búsqueda de música en YouTube
- ✅ Descarga directa a MP3
- ✅ Sin almacenamiento en servidor
- ✅ Interfaz responsive
- ✅ API REST
- ✅ Modo oscuro

---

**¡Tu YouTube MP3 Downloader está listo para el mundo! 🎵**
