# 🎵 YouTube MP3 Downloader

Aplicación web minimalista para buscar y descargar música de YouTube directamente al dispositivo del usuario, **SIN almacenar archivos en el servidor**.

## ✨ Características

- 🔍 **Búsqueda de YouTube**: Busca canciones directamente desde la interfaz
- 📥 **Descarga directa**: Convierte y descarga archivos MP3 (192kbps)
- 🗑️ **Sin almacenamiento**: Los archivos se eliminan automáticamente del servidor
- 🎨 **Diseño minimalista**: Interfaz limpia y moderna con modo oscuro
- 📱 **Responsive**: Funciona perfectamente en móviles y tablets
- ⚡ **Rápido y ligero**: Sin base de datos, sin bibliotecas complejas

## 🛠️ Stack Tecnológico

- **Backend**: Flask (Python)
- **Descarga**: yt-dlp + FFmpeg
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Servidor**: Gunicorn (producción)

## 📋 Requisitos Previos

### Sistema
- Python 3.8 o superior
- FFmpeg instalado en el sistema

### Instalar FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Descarga desde [ffmpeg.org](https://ffmpeg.org/download.html) y añade al PATH

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd /home/emilio/Escritorio/desarrollador/servicio\ descargas
```

### 2. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## ▶️ Uso

### Modo Desarrollo

```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

### Modo Producción con Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Opciones recomendadas:
- `-w 4`: 4 workers
- `-b 0.0.0.0:5000`: Escuchar en todas las interfaces en el puerto 5000
- `--timeout 120`: Timeout de 120 segundos (para descargas largas)

Comando completo recomendado:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

## 📁 Estructura del Proyecto

```
servicio descargas/
├── app.py                  # Aplicación Flask principal
├── requirements.txt        # Dependencias Python
├── README.md              # Documentación
├── cleanup.sh             # Script de limpieza automática
├── templates/
│   └── index.html         # Interfaz de usuario
└── static/
    └── style.css          # Estilos CSS
```

## 🔧 Configuración

### Variables en app.py

```python
TEMP_DIR = '/tmp/youtube_downloads'  # Directorio temporal
MAX_DURATION = 600                   # Duración máxima: 10 minutos
```

### Rate Limiting

Por defecto: 5 descargas por IP por hora

```python
@rate_limiter(max_requests=5, window=3600)
```

## 📡 API Endpoints

### GET /
Página principal con interfaz de búsqueda

### POST /api/search
Buscar videos en YouTube

**Request:**
```json
{
  "query": "nombre de canción"
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "video_id",
      "title": "Título del video",
      "channel": "Nombre del canal",
      "duration": "3:45",
      "thumbnail": "url_thumbnail"
    }
  ]
}
```

### POST /api/download
Descargar y convertir video a MP3

**Request:**
```json
{
  "id": "video_id",
  "title": "Título del video"
}
```

**Response:**
Archivo MP3 como descarga directa

### GET /api/health
Verificar estado del servicio

## 🧹 Limpieza Automática

### Método 1: Cron Job (Recomendado para Linux)

Editar crontab:
```bash
crontab -e
```

Añadir línea para limpiar cada 5 minutos:
```
*/5 * * * * find /tmp/youtube_downloads -type f -mmin +5 -delete
```

### Método 2: Script Manual

Ejecutar el script incluido:
```bash
chmod +x cleanup.sh
./cleanup.sh
```

El script limpia archivos mayores a 5 minutos cada hora.

## 🎨 Características de la Interfaz

- **Búsqueda intuitiva**: Barra de búsqueda grande y visible
- **Resultados en grid**: Vista de tarjetas con thumbnails
- **Información detallada**: Título, canal, duración
- **Botones destacados**: "Descargar MP3" verde llamativo
- **Loading states**: Spinners durante búsqueda y descarga
- **Notificaciones toast**: Feedback visual de acciones
- **Modo oscuro**: Toggle para cambiar tema
- **Responsive**: Adaptado a móviles y tablets

## ⚠️ Limitaciones y Consideraciones

### Legales
- ⚖️ Solo para uso personal
- 📜 Respeta los derechos de autor
- 🚫 No distribuir música con copyright

### Técnicas
- ⏱️ Timeout de 60 segundos por descarga
- 📏 Límite de duración: 10 minutos por video
- 🔒 Rate limiting: 5 descargas/hora por IP
- 💾 Archivos temporales se eliminan automáticamente

## 🐛 Solución de Problemas

### Error: "FFmpeg not found"
```bash
# Verificar instalación
ffmpeg -version

# Si no está instalado, instalar según tu sistema operativo
```

### Error: "Permission denied" en /tmp/youtube_downloads
```bash
# Crear directorio con permisos
sudo mkdir -p /tmp/youtube_downloads
sudo chmod 777 /tmp/youtube_downloads
```

### Error: "Rate limit exceeded"
Espera una hora o modifica el rate limit en `app.py`

### La descarga no inicia
- Verifica que la URL de YouTube sea válida
- Comprueba que el video no esté restringido geográficamente
- Revisa que la duración sea menor a 10 minutos

## 📝 Notas de Desarrollo

### Proceso de Descarga

1. Usuario busca canción
2. Resultados se muestran en grid
3. Click en "Descargar MP3"
4. Servidor descarga con yt-dlp
5. FFmpeg convierte a MP3 (192kbps)
6. Archivo se envía al navegador
7. Servidor elimina archivo temporal

### Seguridad

- ✅ Sanitización de nombres de archivo
- ✅ Rate limiting por IP
- ✅ Validación de URLs de YouTube
- ✅ Timeout en descargas
- ✅ Limpieza automática de archivos

## 🚀 Deploy en Producción

### Con systemd (Linux)

Crear servicio: `/etc/systemd/system/youtube-downloader.service`

```ini
[Unit]
Description=YouTube MP3 Downloader
After=network.target

[Service]
User=www-data
WorkingDirectory=/home/emilio/Escritorio/desarrollador/servicio descargas
Environment="PATH=/home/emilio/Escritorio/desarrollador/servicio descargas/venv/bin"
ExecStart=/home/emilio/Escritorio/desarrollador/servicio descargas/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app

[Install]
WantedBy=multi-user.target
```

Activar servicio:
```bash
sudo systemctl enable youtube-downloader
sudo systemctl start youtube-downloader
```

### Con Nginx (Reverse Proxy)

Configuración nginx:
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 120s;
    }
}
```

## 📊 Monitoreo

Verificar estado del servicio:
```bash
curl http://localhost:5000/api/health
```

Ver archivos temporales:
```bash
ls -lh /tmp/youtube_downloads/
```

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso personal.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📧 Soporte

Para reportar problemas o sugerencias, abre un issue en el repositorio.

---

**⚡ Hecho con Flask y ❤️**
