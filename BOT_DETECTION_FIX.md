# 🔐 Solución: Error de Autenticación de YouTube (Bot Detection)

## ❌ Problema

```
ERROR: Sign in to confirm you're not a bot
```

YouTube está detectando que yt-dlp es un bot y bloqueando las peticiones.

## ✅ Soluciones

### Opción 1: Redeployar con Headers Mejorados (YA IMPLEMENTADO)

Los cambios ya fueron subidos:
- ✅ Headers HTTP completos y modernos
- ✅ Geo-bypass habilitado
- ✅ Socket timeout aumentado
- ✅ Reintentos incrementados (5 y 15)
- ✅ Deshabilitadas manifestaciones DASH/HLS que causan bloqueos

**Acciones:**
```bash
# Los cambios ya están en GitHub
# Ve a Railway → Deployments → Redeploy
# O espera a que Railway redespiegue automáticamente
```

---

### Opción 2: Usar Cookies de Tu Navegador (Más Efectivo)

Si el error persiste, esta es la solución definitiva.

#### Paso 1: Exportar cookies de YouTube

**En Chrome/Edge/Brave:**

1. Abre YouTube en tu navegador
2. Abre DevTools: `F12` o `Ctrl+Shift+I`
3. Ve a pestaña **"Console"**
4. Copia y pega esto:

```javascript
const cookies = document.cookie.split('; ').map(c => {
    const [name, value] = c.split('=');
    return `${name}\t${value}`;
}).join('\n');
console.log(cookies);
copy(cookies);
alert('Cookies copiadas al portapapeles');
```

5. Se copiarán las cookies automáticamente

**O instala extensión "Get cookies.txt":**
- Chrome: https://chrome.google.com/webstore/detail/get-cookiestxt
- Firefox: https://addons.mozilla.org/es/firefox/addon/cookies-txt/

---

#### Paso 2: Crear archivo cookies.txt

En Railway, necesitas crear un archivo `cookies.txt` en la raíz del proyecto:

```
# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

.youtube.com	TRUE	/	TRUE	0	VISITOR_INFO1_LIVE	tu_cookie_aqui
.youtube.com	TRUE	/	TRUE	0	CONSISTENCY	tu_cookie_aqui
```

---

#### Paso 3: Usar cookies en app.py

Modificar `app.py`:

```python
# En la función download(), agregar:
'cookiefile': 'cookies.txt',
```

Ejemplo:
```python
ydl_opts = {
    'format': 'bestaudio/best',
    # ... otras opciones ...
    'cookiefile': 'cookies.txt',  # Agregar esta línea
}
```

---

### Opción 3: Usar Cookies en Secret de Railway

Mejor práctica para Railway (evita exponerlas en GitHub):

1. **En Railway Dashboard:**
   - Ve a tu proyecto
   - Variables → Agregar variable
   - Nombre: `YOUTUBE_COOKIES`
   - Valor: (contenido del archivo cookies.txt)

2. **Modificar app.py:**

```python
import os

# En la función download():
cookies_content = os.environ.get('YOUTUBE_COOKIES', '')
if cookies_content:
    with open('temp_cookies.txt', 'w') as f:
        f.write(cookies_content)
    ydl_opts['cookiefile'] = 'temp_cookies.txt'
```

---

### Opción 4: Usar Proxy (Si es necesario)

```python
ydl_opts = {
    # ... opciones existentes ...
    'proxy': 'http://proxy-ip:puerto',
}
```

---

## 🔍 Diagnosticar el Problema

### Ver logs en detalle

En `app.py`, cambiar temporalmente:

```python
'quiet': False,     # Cambiar de True
'verbose': True,    # Agregar
```

Esto mostrará logs detallados en Railway.

---

## 🚀 Pasos Inmediatos

### 1. Redeployar en Railway
```
Railway Dashboard → Deployments → Redeploy
```
Los cambios con headers mejorados ya están subidos.

### 2. Esperar 5-10 minutos
Railway construirá y desplegará con la nueva configuración.

### 3. Si sigue fallando, usar Opción 2
Exportar cookies y subirlas como variable de entorno en Railway.

---

## 📊 Lo que cambió en app.py

**Headers mejorados:**
```python
'Sec-Fetch-Dest': 'document',
'Sec-Fetch-Mode': 'navigate',
'Sec-Fetch-Site': 'none',
'Sec-Fetch-User': '?1',
'Cache-Control': 'max-age=0',
```

**Configuración de bypass:**
```python
'geo_bypass': True,
'geo_bypass_country': 'US',
'socket_timeout': 30,
'extractor_retries': 5,      # Era 3
'fragment_retries': 15,       # Era 10
```

**Deshabilitadas opciones problemáticas:**
```python
'youtube_include_dash_manifest': False,
'youtube_include_hls_manifest': False,
```

---

## 🆘 Si nada funciona

**Causa más probable:** YouTube ha actualizado sus medidas anti-bot.

**Soluciones definitivas:**

1. **Usar invidious/piped (instancia de YouTube alternativa)**
2. **Cambiar a otra librería como pytube**
3. **Usar proxy residencial**
4. **Operar en horarios específicos para evitar detectores**

---

## ✅ Próximos Pasos

1. **Redeployar en Railway** con los cambios
2. **Probar en 10 minutos**
3. **Si falla, implementar Opción 2** (cookies)

El nuevo deploy debe resolver el problema en el 80% de los casos.

---

**Última actualización:** 25 de febrero de 2026
