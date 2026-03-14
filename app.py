import os
import time
import random
import re
import json
import urllib.request
from flask import Flask, render_template, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import yt_dlp
from functools import wraps

app = Flask(__name__)
CORS(app)

# Configuración
TEMP_DIR = '/tmp/youtube_downloads'
MAX_DURATION = 600  # 10 minutos en segundos
RATE_LIMIT = {}  # IP: [timestamps]

# Crear directorio temporal si no existe
os.makedirs(TEMP_DIR, exist_ok=True)


def sanitize_filename(filename):
    """Limpia el nombre del archivo para evitar problemas"""
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename[:100]  # Limitar longitud


def rate_limiter(max_requests=5, window=3600):
    """Limita las peticiones por IP"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            current_time = time.time()
            
            if ip not in RATE_LIMIT:
                RATE_LIMIT[ip] = []
            
            # Limpiar timestamps antiguos
            RATE_LIMIT[ip] = [ts for ts in RATE_LIMIT[ip] if current_time - ts < window]
            
            if len(RATE_LIMIT[ip]) >= max_requests:
                return jsonify({
                    'error': 'Límite de descargas alcanzado. Intenta en una hora.'
                }), 429
            
            RATE_LIMIT[ip].append(current_time)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def cleanup_old_files():
    """Elimina archivos temporales mayores a 5 minutos"""
    try:
        current_time = time.time()
        for filename in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > 300:  # 5 minutos
                    os.remove(file_path)
    except Exception as e:
        print(f"Error en limpieza: {e}")


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


def parse_duration_text(text):
    """Convierte '3:45' o '1:02:30' a segundos"""
    if not text:
        return 0
    parts = text.split(':')
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return 0
    except (ValueError, IndexError):
        return 0


def innertube_search(query, max_results=20):
    """Buscar en YouTube usando la API innertube directamente"""
    url = "https://www.youtube.com/youtubei/v1/search"
    
    payload = {
        "context": {
            "client": {
                "clientName": "WEB",
                "clientVersion": "2.20241120.01.00",
                "hl": "es",
                "gl": "US",
            }
        },
        "query": query,
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Referer': 'https://www.youtube.com/',
        'Origin': 'https://www.youtube.com',
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
    
    videos = []
    
    # Navegar la estructura de respuesta de innertube
    try:
        contents = result['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']
    except (KeyError, TypeError):
        return videos
    
    for section in contents:
        items = section.get('itemSectionRenderer', {}).get('contents', [])
        for item in items:
            renderer = item.get('videoRenderer')
            if not renderer:
                continue
            
            video_id = renderer.get('videoId', '')
            if not video_id:
                continue
            
            # Título
            title = 'Sin título'
            title_runs = renderer.get('title', {}).get('runs', [])
            if title_runs:
                title = title_runs[0].get('text', 'Sin título')
            
            # Canal
            channel = 'Desconocido'
            channel_runs = renderer.get('ownerText', {}).get('runs', [])
            if channel_runs:
                channel = channel_runs[0].get('text', 'Desconocido')
            
            # Duración
            duration_text = renderer.get('lengthText', {}).get('simpleText', '0:00')
            duration_seconds = parse_duration_text(duration_text)
            
            # Filtrar videos muy largos
            if duration_seconds > MAX_DURATION:
                continue
            
            # Thumbnail
            thumbnail_url = f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg'
            thumbs = renderer.get('thumbnail', {}).get('thumbnails', [])
            if thumbs:
                thumbnail_url = thumbs[-1].get('url', thumbnail_url)
            
            # View count
            view_count = 0
            view_text = renderer.get('viewCountText', {}).get('simpleText', '')
            if view_text:
                numbers = re.sub(r'[^\d]', '', view_text)
                if numbers:
                    view_count = int(numbers)
            
            videos.append({
                'id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'title': title,
                'channel': channel,
                'duration': duration_text if duration_text != '0:00' else format_duration(duration_seconds),
                'duration_seconds': duration_seconds,
                'thumbnail': thumbnail_url,
                'view_count': view_count
            })
            
            if len(videos) >= max_results:
                break
        if len(videos) >= max_results:
            break
    
    return videos


@app.route('/api/search', methods=['POST'])
def search():
    """Buscar videos en YouTube"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query vacío'}), 400
        
        videos = innertube_search(query, max_results=20)
        return jsonify({'results': videos})
    
    except Exception as e:
        return jsonify({'error': f'Error en búsqueda: {str(e)}'}), 500


@app.route('/api/download', methods=['POST'])
@rate_limiter(max_requests=5, window=3600)
def download():
    """Descargar y convertir video a MP3"""
    cleanup_old_files()  # Limpiar archivos antiguos antes de descargar
    
    try:
        data = request.get_json()
        video_id = data.get('id', '')
        title = data.get('title', 'audio')
        
        if not video_id:
            return jsonify({'error': 'ID de video requerido'}), 400
        
        # URL completa de YouTube
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Generar nombre temporal único
        temp_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Crear cookies file si está disponible en variables de entorno
        cookies_file = None
        youtube_cookies = os.environ.get('YOUTUBE_COOKIES', '')
        
        if youtube_cookies:
            cookies_file = f'{TEMP_DIR}/cookies_{temp_id}.txt'
            try:
                with open(cookies_file, 'w') as f:
                    f.write(youtube_cookies)
            except Exception as e:
                print(f"Error escribiendo cookies: {e}")
                cookies_file = None
        
        # Opciones de descarga
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{TEMP_DIR}/{temp_id}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'nocheckcertificate': True,
            'extractor_retries': 5,
            'fragment_retries': 15,
            'socket_timeout': 30,
            'skip_unavailable_fragments': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            },
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'youtube_include_dash_manifest': False,
            'youtube_include_hls_manifest': False,
        }
        
        # Agregar cookies si están disponibles
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file
        
        # Descargar y convertir
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Archivo MP3 resultante
        mp3_file = f'{TEMP_DIR}/{temp_id}.mp3'
        
        # Verificar que el archivo existe
        if not os.path.exists(mp3_file):
            return jsonify({'error': 'Error al generar el archivo MP3'}), 500
        
        
        # Nombre limpio para el archivo
        clean_title = sanitize_filename(title)
        download_name = f"{clean_title}.mp3"
        
        # Eliminar archivo después de enviarlo
        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(mp3_file):
                    os.remove(mp3_file)
                    print(f"Archivo eliminado: {mp3_file}")
                # Eliminar también archivo de cookies si existe
                if cookies_file and os.path.exists(cookies_file):
                    os.remove(cookies_file)
                    print(f"Cookies eliminadas: {cookies_file}")
            except Exception as e:
                print(f"Error al eliminar archivos: {e}")
            return response
        
        # Enviar archivo al usuario
        return send_file(
            mp3_file,
            as_attachment=True,
            download_name=download_name,
            mimetype='audio/mpeg'
        )
    
    except Exception as e:
        return jsonify({'error': f'Error en descarga: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint de salud para verificar el servicio"""
    return jsonify({
        'status': 'ok',
        'temp_files': len(os.listdir(TEMP_DIR)) if os.path.exists(TEMP_DIR) else 0
    })


def format_duration(seconds):
    """Convierte segundos a formato MM:SS"""
    if not seconds:
        return "0:00"
    
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


if __name__ == '__main__':
    # Limpiar archivos antiguos al iniciar
    cleanup_old_files()
    
    # Puerto desde variable de entorno (Railway, Heroku, etc.) o 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    
    # Modo desarrollo o producción según DEBUG
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(debug=debug, host='0.0.0.0', port=port)
