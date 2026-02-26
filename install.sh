#!/bin/bash

# Script de instalación rápida para YouTube MP3 Downloader
# Este script configura el entorno y instala las dependencias necesarias

set -e  # Salir si hay algún error

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=========================================="
echo " YouTube MP3 Downloader - Instalación"
echo "=========================================="
echo -e "${NC}"

# Verificar Python
echo -e "${YELLOW}[1/6] Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 no está instalado${NC}"
    echo "Por favor instala Python 3.8 o superior"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ $PYTHON_VERSION encontrado${NC}"

# Verificar FFmpeg
echo -e "${YELLOW}[2/6] Verificando FFmpeg...${NC}"
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}Error: FFmpeg no está instalado${NC}"
    echo "Por favor instala FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    exit 1
fi
FFMPEG_VERSION=$(ffmpeg -version | head -n 1)
echo -e "${GREEN}✓ FFmpeg encontrado${NC}"

# Crear entorno virtual
echo -e "${YELLOW}[3/6] Creando entorno virtual...${NC}"
if [ -d "venv" ]; then
    echo "El entorno virtual ya existe, omitiendo..."
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Entorno virtual creado${NC}"
fi

# Activar entorno virtual
echo -e "${YELLOW}[4/6] Activando entorno virtual...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Entorno virtual activado${NC}"

# Instalar dependencias
echo -e "${YELLOW}[5/6] Instalando dependencias...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencias instaladas${NC}"

# Crear directorio temporal
echo -e "${YELLOW}[6/6] Configurando directorios...${NC}"
sudo mkdir -p /tmp/youtube_downloads
sudo chmod 777 /tmp/youtube_downloads
echo -e "${GREEN}✓ Directorio temporal creado${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo "  ✓ Instalación completada con éxito"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}Para iniciar la aplicación:${NC}"
echo ""
echo -e "  ${YELLOW}Modo desarrollo:${NC}"
echo "    python app.py"
echo ""
echo -e "  ${YELLOW}Modo producción:${NC}"
echo "    gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app"
echo ""
echo -e "${BLUE}La aplicación estará disponible en:${NC}"
echo "  http://localhost:5000"
echo ""
echo -e "${BLUE}Para configurar limpieza automática:${NC}"
echo "  crontab -e"
echo "  # Agregar: */5 * * * * find /tmp/youtube_downloads -type f -mmin +5 -delete"
echo ""
