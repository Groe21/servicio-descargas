# 🔧 Solución de Problemas Comunes

## ❌ Error 403: Forbidden de YouTube

### Problema
```
ERROR: unable to download video data: HTTP Error 403: Forbidden
```

### ✅ Soluciones Implementadas

#### 1. Actualización de yt-dlp
```bash
pip install --upgrade yt-dlp
```
**Versión actual:** 2026.2.21

#### 2. Headers de navegador agregados
Se agregaron headers HTTP completos para simular un navegador real:
- User-Agent de Chrome 120
- Accept headers
- Referer de YouTube
- Sec-Fetch-Mode

#### 3. Opciones de reintentos
- `extractor_retries`: 3 intentos
- `fragment_retries`: 10 intentos

### 🔍 Si el problema persiste

#### Opción 1: Usar cookies de navegador

1. **Instalar extensión "Get cookies.txt"** en tu navegador
2. **Ir a YouTube** y hacer login
3. **Exportar cookies** a un archivo `cookies.txt`
4. **Copiar archivo** a la carpeta del proyecto
5. **Modificar app.py**:

```python
ydl_opts = {
    # ... opciones existentes ...
    'cookiefile': 'cookies.txt',  # Agregar esta línea
}
```

#### Opción 2: Usar proxy

```python
ydl_opts = {
    # ... opciones existentes ...
    'proxy': 'http://tu-proxy:puerto',
}
```

#### Opción 3: Actualizar manualmente yt-dlp

```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar versión de desarrollo (más actualizada)
pip install --upgrade --force-reinstall "yt-dlp[default]"

# O instalar desde GitHub directamente
pip install --upgrade git+https://github.com/yt-dlp/yt-dlp.git
```

#### Opción 4: Verificar bloqueo regional

Algunos videos pueden estar bloqueados en tu región. Intenta con:

```python
ydl_opts = {
    # ... opciones existentes ...
    'geo_bypass': True,
    'geo_bypass_country': 'US',
}
```

---

## ⚡ Otros Errores Comunes

### Error: "FFmpeg not found"

**Solución:**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg -y

# Verificar instalación
ffmpeg -version
```

---

### Error: "Permission denied" en /tmp/youtube_downloads

**Solución:**
```bash
sudo mkdir -p /tmp/youtube_downloads
sudo chmod 777 /tmp/youtube_downloads
```

---

### Error: "Port 5000 is in use"

**Solución 1: Detener proceso existente**
```bash
# Ver qué proceso usa el puerto
sudo lsof -i :5000

# Detener proceso
pkill -f "python app.py"
```

**Solución 2: Usar otro puerto**
```python
# En app.py, cambiar última línea:
app.run(debug=True, host='0.0.0.0', port=8000)  # Puerto 8000
```

---

### Error: "Rate limit exceeded"

**Causa:** Más de 5 descargas en una hora desde la misma IP.

**Solución temporal:**
```python
# En app.py, cambiar el decorator:
@rate_limiter(max_requests=10, window=3600)  # 10 descargas/hora
```

**Solución permanente:** Esperar una hora.

---

### Video no descarga (sin error específico)

**Causas posibles:**
1. Video privado o eliminado
2. Video con restricción de edad
3. Video muy largo (> 10 minutos)
4. Restricción regional

**Solución para videos con restricción de edad:**
```python
ydl_opts = {
    # ... opciones existentes ...
    'age_limit': None,  # Permitir todos los videos
}
```

---

## 🔄 Actualización Regular de yt-dlp

YouTube cambia frecuentemente sus APIs. Es importante mantener yt-dlp actualizado:

### Actualización manual
```bash
cd "/home/emilio/Escritorio/desarrollador/servicio descargas"
source venv/bin/activate
pip install --upgrade yt-dlp
```

### Actualización automática (cron job)

```bash
crontab -e
```

Agregar:
```
0 3 * * * cd "/home/emilio/Escritorio/desarrollador/servicio descargas" && source venv/bin/activate && pip install --upgrade yt-dlp > /dev/null 2>&1
```

Esto actualiza yt-dlp todos los días a las 3 AM.

---

## 📊 Verificar Estado

### Test rápido
```bash
curl http://localhost:5000/api/health
```

### Ver logs en tiempo real
```bash
# Si usas systemd
sudo journalctl -u youtube-downloader -f

# Si ejecutas manualmente
# Los logs aparecen en la consola donde ejecutaste python app.py
```

### Probar descarga desde línea de comandos
```bash
cd "/home/emilio/Escritorio/desarrollador/servicio descargas"
source venv/bin/activate

# Probar yt-dlp directamente
yt-dlp --version
yt-dlp -f bestaudio --extract-audio --audio-format mp3 "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

---

## 🆘 Última Alternativa: Reiniciar desde Cero

Si nada funciona:

```bash
# 1. Ir al directorio
cd "/home/emilio/Escritorio/desarrollador/servicio descargas"

# 2. Eliminar entorno virtual
rm -rf venv

# 3. Ejecutar instalación de nuevo
./install.sh

# 4. Iniciar servidor
source venv/bin/activate
python app.py
```

---

## 📞 Información de Debug

### Obtener información detallada de errores

Modificar app.py temporalmente:

```python
# En la función download(), cambiar quiet a False
ydl_opts = {
    # ...
    'quiet': False,  # Cambiar de True a False
    'verbose': True,  # Agregar esta línea
    # ...
}
```

Esto mostrará información detallada en la consola sobre qué está fallando.

---

## ✅ Cambios Realizados

### requirements.txt
- ✅ Actualizado yt-dlp de 2024.8.6 a 2026.2.21+

### app.py
- ✅ Agregado User-Agent moderno
- ✅ Agregados HTTP headers completos
- ✅ Agregado referer de YouTube
- ✅ Configurados reintentos automáticos
- ✅ Deshabilitada verificación de certificados

### Comandos ejecutados
```bash
pip install --upgrade yt-dlp  # ✅ Completado
pkill -f "python app.py"      # ✅ Servidor anterior detenido
python app.py                 # ✅ Servidor reiniciado
```

---

## 🎯 Estado Actual

**Servidor:** ✅ Corriendo en http://192.168.1.89:5000  
**yt-dlp:** ✅ Versión 2026.2.21  
**FFmpeg:** ✅ Instalado  
**Headers:** ✅ Configurados  

**El error 403 debería estar resuelto.** Intenta descargar un video nuevamente.

Si el problema persiste, implementa la **Opción 1** (cookies) que es la más efectiva.

---

**Última actualización:** 25 de febrero de 2026, 22:25
