#!/bin/bash

# Script para extraer cookies de YouTube y guardarlas

echo "=========================================="
echo "   Extractor de Cookies de YouTube"
echo "=========================================="
echo ""
echo "Instrucciones:"
echo "1. Abre YouTube en tu navegador Chrome/Firefox"
echo "2. Abre DevTools (F12)"
echo "3. Ve a Console"
echo "4. Copia y ejecuta:"
echo ""
echo "// Para Chrome/Edge:"
echo "const cookies = document.cookie.split('; ').map(c => {"
echo "    const [name, value] = c.split('=');"
echo "    return name + '=' + value;"
echo "}).join('; ');"
echo "copy(cookies);"
echo ""
echo "5. O usa la extensión: Get cookies.txt"
echo ""
echo "Después de copiar las cookies, pega aquí:"
read -p "Cookies (Ctrl+Shift+V): " cookies

if [ -z "$cookies" ]; then
    echo "Error: No se ingresaron cookies"
    exit 1
fi

# Crear archivo cookies.txt
cat > cookies.txt << 'EOF'
# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

EOF

# Procesar cookies en formato Netscape
IFS=';' read -ra COOKIES <<< "$cookies"
for cookie in "${COOKIES[@]}"; do
    cookie=$(echo "$cookie" | sed 's/^ *//;s/ *$//')
    if [ ! -z "$cookie" ]; then
        IFS='=' read -ra PARTS <<< "$cookie"
        name="${PARTS[0]}"
        value="${PARTS[1]}"
        echo ".youtube.com	TRUE	/	TRUE	0	$name	$value" >> cookies.txt
    fi
done

echo ""
echo "✅ Cookies guardadas en: cookies.txt"
echo ""
echo "Ahora en app.py se utilizarán automáticamente para descargas."
