#!/bin/bash

# Script de limpieza automática para YouTube MP3 Downloader
# Elimina archivos temporales mayores a 5 minutos

TEMP_DIR="/tmp/youtube_downloads"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== YouTube MP3 Downloader - Limpieza Automática ===${NC}"
echo "Directorio: $TEMP_DIR"
echo "Eliminando archivos mayores a 5 minutos..."

# Crear directorio si no existe
mkdir -p "$TEMP_DIR"

# Contar archivos antes de limpiar
FILES_BEFORE=$(find "$TEMP_DIR" -type f 2>/dev/null | wc -l)
echo "Archivos encontrados: $FILES_BEFORE"

# Eliminar archivos mayores a 5 minutos
find "$TEMP_DIR" -type f -mmin +5 -delete 2>/dev/null

# Contar archivos después de limpiar
FILES_AFTER=$(find "$TEMP_DIR" -type f 2>/dev/null | wc -l)
FILES_DELETED=$((FILES_BEFORE - FILES_AFTER))

echo -e "${GREEN}Archivos eliminados: $FILES_DELETED${NC}"
echo -e "${YELLOW}Archivos restantes: $FILES_AFTER${NC}"
echo "Limpieza completada."
