# 📡 Ejemplos de Uso de la API

Este documento muestra cómo usar la API de YouTube MP3 Downloader mediante ejemplos prácticos.

## 🔍 Endpoints Disponibles

### 1. Health Check
### 2. Búsqueda de Videos
### 3. Descarga de MP3

---

## 1. 🏥 Health Check

Verifica que el servicio esté funcionando correctamente.

**Endpoint:** `GET /api/health`

### Ejemplo con cURL:

```bash
curl http://localhost:5000/api/health
```

### Respuesta:

```json
{
  "status": "ok",
  "temp_files": 0
}
```

---

## 2. 🔍 Búsqueda de Videos

Busca videos en YouTube por término de búsqueda.

**Endpoint:** `POST /api/search`

### Ejemplo con cURL:

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "beethoven symphony"}'
```

### Ejemplo con Python:

```python
import requests

url = "http://localhost:5000/api/search"
data = {"query": "beethoven symphony"}

response = requests.post(url, json=data)
results = response.json()

for video in results['results']:
    print(f"{video['title']} - {video['duration']}")
```

### Ejemplo con JavaScript (Fetch):

```javascript
fetch('http://localhost:5000/api/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'beethoven symphony'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Resultados:', data.results);
});
```

### Respuesta de ejemplo:

```json
{
  "results": [
    {
      "id": "dQw4w9WgXcQ",
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "title": "Beethoven - Symphony No. 9",
      "channel": "ClassicalMusic",
      "duration": "5:45",
      "duration_seconds": 345,
      "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      "view_count": 1000000
    },
    {
      "id": "abc123xyz",
      "url": "https://www.youtube.com/watch?v=abc123xyz",
      "title": "Beethoven - Symphony No. 5",
      "channel": "OrchestraChannel",
      "duration": "7:20",
      "duration_seconds": 440,
      "thumbnail": "https://i.ytimg.com/vi/abc123xyz/maxresdefault.jpg",
      "view_count": 500000
    }
  ]
}
```

---

## 3. 📥 Descarga de MP3

Descarga y convierte un video de YouTube a MP3.

**Endpoint:** `POST /api/download`

### Ejemplo con cURL:

```bash
curl -X POST http://localhost:5000/api/download \
  -H "Content-Type: application/json" \
  -d '{"id": "dQw4w9WgXcQ", "title": "Beethoven Symphony No 9"}' \
  --output "beethoven.mp3"
```

### Ejemplo con Python:

```python
import requests

url = "http://localhost:5000/api/download"
data = {
    "id": "dQw4w9WgXcQ",
    "title": "Beethoven Symphony No 9"
}

response = requests.post(url, json=data)

if response.status_code == 200:
    with open("beethoven.mp3", "wb") as f:
        f.write(response.content)
    print("Descarga completada!")
else:
    print(f"Error: {response.json()}")
```

### Ejemplo con JavaScript (Fetch):

```javascript
fetch('http://localhost:5000/api/download', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    id: 'dQw4w9WgXcQ',
    title: 'Beethoven Symphony No 9'
  })
})
.then(response => response.blob())
.then(blob => {
  // Crear enlace de descarga
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'beethoven.mp3';
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
});
```

### Ejemplo con wget:

```bash
wget --post-data='{"id":"dQw4w9WgXcQ","title":"Beethoven"}' \
  --header='Content-Type: application/json' \
  http://localhost:5000/api/download \
  -O beethoven.mp3
```

---

## 🔄 Workflow Completo

### Ejemplo en Python:

```python
import requests

BASE_URL = "http://localhost:5000"

def search_and_download(query, download_first=True):
    """Busca y descarga el primer resultado"""
    
    # 1. Buscar videos
    print(f"Buscando: {query}...")
    search_response = requests.post(
        f"{BASE_URL}/api/search",
        json={"query": query}
    )
    
    if search_response.status_code != 200:
        print("Error en búsqueda")
        return
    
    results = search_response.json()['results']
    
    if not results:
        print("No se encontraron resultados")
        return
    
    # 2. Mostrar resultados
    print(f"\nEncontrados {len(results)} resultados:")
    for i, video in enumerate(results[:5], 1):
        print(f"{i}. {video['title']} - {video['duration']}")
    
    # 3. Descargar primer resultado
    if download_first:
        video = results[0]
        print(f"\nDescargando: {video['title']}...")
        
        download_response = requests.post(
            f"{BASE_URL}/api/download",
            json={
                "id": video['id'],
                "title": video['title']
            }
        )
        
        if download_response.status_code == 200:
            filename = f"{video['title'][:50]}.mp3"
            with open(filename, "wb") as f:
                f.write(download_response.content)
            print(f"✓ Descargado: {filename}")
        else:
            print(f"✗ Error: {download_response.json()}")

# Usar la función
search_and_download("lo-fi hip hop")
```

### Ejemplo en Bash:

```bash
#!/bin/bash

# Buscar música
QUERY="beethoven symphony"
SEARCH_RESULT=$(curl -s -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\"}")

# Extraer primer ID (requiere jq)
VIDEO_ID=$(echo $SEARCH_RESULT | jq -r '.results[0].id')
VIDEO_TITLE=$(echo $SEARCH_RESULT | jq -r '.results[0].title')

echo "Descargando: $VIDEO_TITLE"

# Descargar
curl -X POST http://localhost:5000/api/download \
  -H "Content-Type: application/json" \
  -d "{\"id\": \"$VIDEO_ID\", \"title\": \"$VIDEO_TITLE\"}" \
  --output "${VIDEO_TITLE}.mp3"

echo "Descarga completada!"
```

---

## ⚠️ Manejo de Errores

### Respuestas de Error Comunes:

#### Query vacío (búsqueda):
```json
{
  "error": "Query vacío"
}
```
**Status:** 400

#### ID de video requerido (descarga):
```json
{
  "error": "ID de video requerido"
}
```
**Status:** 400

#### Rate limit excedido:
```json
{
  "error": "Límite de descargas alcanzado. Intenta en una hora."
}
```
**Status:** 429

#### Error en descarga:
```json
{
  "error": "Error en descarga: [mensaje de error]"
}
```
**Status:** 500

---

## 🔒 Consideraciones de Seguridad

### Rate Limiting

Por defecto: **5 descargas por IP por hora**

Para cambiar, modifica en `app.py`:
```python
@rate_limiter(max_requests=10, window=3600)  # 10 descargas por hora
```

### Validación de Duración

Videos mayores a 10 minutos son filtrados automáticamente.

---

## 📊 Monitoreo de Uso

### Script de monitoreo:

```python
import requests
import time

def monitor_service():
    """Monitorea el estado del servicio"""
    while True:
        try:
            response = requests.get("http://localhost:5000/api/health")
            data = response.json()
            print(f"[{time.strftime('%H:%M:%S')}] Status: {data['status']} | "
                  f"Temp files: {data['temp_files']}")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Error: {e}")
        
        time.sleep(60)  # Verificar cada minuto

monitor_service()
```

---

## 🧪 Testing

### Test de búsqueda:

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}' | jq
```

### Test de health:

```bash
curl http://localhost:5000/api/health | jq
```

### Test completo con Python:

```python
import requests
import time

def test_full_workflow():
    base_url = "http://localhost:5000"
    
    # Test 1: Health check
    print("Test 1: Health check...")
    response = requests.get(f"{base_url}/api/health")
    assert response.status_code == 200
    print("✓ Health check OK")
    
    # Test 2: Search
    print("\nTest 2: Search...")
    response = requests.post(
        f"{base_url}/api/search",
        json={"query": "short music"}
    )
    assert response.status_code == 200
    results = response.json()['results']
    assert len(results) > 0
    print(f"✓ Search OK ({len(results)} results)")
    
    # Test 3: Download (primer resultado)
    print("\nTest 3: Download...")
    video = results[0]
    response = requests.post(
        f"{base_url}/api/download",
        json={
            "id": video['id'],
            "title": "test_download"
        }
    )
    assert response.status_code == 200
    print(f"✓ Download OK ({len(response.content)} bytes)")
    
    print("\n✓ All tests passed!")

test_full_workflow()
```

---

## 📚 Recursos Adicionales

- [README.md](README.md) - Documentación principal
- [DEPLOYMENT.md](DEPLOYMENT.md) - Guía de despliegue
- [app.py](app.py) - Código fuente del backend
- [templates/index.html](templates/index.html) - Frontend

---

**🎵 ¡Disfruta descargando música de forma responsable!**
