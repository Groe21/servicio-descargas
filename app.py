import os
import time
import random
import re
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


@app.route('/api/search', methods=['POST'])
def search():
    """Buscar videos en YouTube"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query vacío'}), 400
        
        # Crear cookies file si está disponible en variables de entorno
        cookies_file = None
        youtube_cookies = os.environ.get('YOUTUBE_COOKIES', '')
        
        if youtube_cookies:
            temp_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
            cookies_file = f'{TEMP_DIR}/search_cookies_{temp_id}.txt'
            try:
                with open(cookies_file, 'w') as f:
                    f.write(youtube_cookies)
            except Exception as e:
                print(f"Error escribiendo cookies para búsqueda: {e}")
                cookies_file = None
        
        # Opciones de búsqueda con yt-dlp
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'force_generic_extractor': False,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'geo_bypass': True,
            'socket_timeout': 30,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
            },
        }
        
        # Agregar cookies si están disponibles
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Buscar en YouTube
            search_query = f"ytsearch20:{query}"
            result = ydl.extract_info(search_query, download=False)
            
            if not result or 'entries' not in result:
                return jsonify({'results': []})
            
            # Formatear resultados
            videos = []
            for entry in result['entries']:
                if entry:
                    duration = entry.get('duration', 0)
                    
                    # Filtrar videos muy largos
                    if duration > MAX_DURATION:
                        continue
                    
                    videos.append({
                        'id': entry.get('id', ''),
                        'url': entry.get('url', ''),
                        'title': entry.get('title', 'Sin título'),
                        'channel': entry.get('uploader', entry.get('channel', 'Desconocido')),
                        'duration': format_duration(duration),
                        'duration_seconds': duration,
                        'thumbnail': entry.get('thumbnail', ''),
                        'view_count': entry.get('view_count', 0)
                    })
            
            return jsonify({'results': videos[:20]})
    
    except Exception as e:
        return jsonify({'error': f'Error en búsqueda: {str(e)}'}), 500
    finally:
        # Limpiar archivo de cookies si existe
        if 'cookies_file' in locals() and cookies_file and os.path.exists(cookies_file):
            try:
                os.remove(cookies_file)
            except:
                pass


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
