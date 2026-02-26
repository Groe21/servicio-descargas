# 🚀 Guía de Despliegue Rápido

## 📝 Pre-requisitos

- Servidor Linux (Ubuntu/Debian recomendado)
- Acceso root o sudo
- Dominio apuntando al servidor (opcional)

## ⚡ Instalación Rápida (5 minutos)

### 1. Instalar dependencias del sistema

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python, pip y FFmpeg
sudo apt install -y python3 python3-pip python3-venv ffmpeg nginx
```

### 2. Clonar o copiar el proyecto

```bash
# Ir al directorio de proyectos
cd /var/www/

# Copiar tu proyecto aquí
sudo cp -r "/home/emilio/Escritorio/desarrollador/servicio descargas" youtube-downloader

# Cambiar propietario
sudo chown -R www-data:www-data youtube-downloader
cd youtube-downloader
```

### 3. Ejecutar instalación automática

```bash
# Dar permisos de ejecución
chmod +x install.sh

# Ejecutar instalación
./install.sh
```

### 4. Configurar servicio systemd

```bash
# Copiar archivo de servicio
sudo cp youtube-downloader.service /etc/systemd/system/

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicio
sudo systemctl enable youtube-downloader

# Iniciar servicio
sudo systemctl start youtube-downloader

# Verificar estado
sudo systemctl status youtube-downloader
```

### 5. Configurar Nginx (opcional)

```bash
# Copiar configuración
sudo cp nginx.conf.example /etc/nginx/sites-available/youtube-downloader

# Editar dominio
sudo nano /etc/nginx/sites-available/youtube-downloader
# Cambiar "tu-dominio.com" por tu dominio real

# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/youtube-downloader /etc/nginx/sites-enabled/

# Probar configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx
```

### 6. Configurar limpieza automática

```bash
# Editar crontab
crontab -e

# Agregar línea para limpieza cada 5 minutos:
*/5 * * * * find /tmp/youtube_downloads -type f -mmin +5 -delete
```

## ✅ Verificación

### Comprobar que todo funciona:

```bash
# 1. Verificar servicio
sudo systemctl status youtube-downloader

# 2. Verificar puerto
curl http://localhost:5000/api/health

# 3. Ver logs
sudo journalctl -u youtube-downloader -f
```

## 🔒 Configurar SSL con Let's Encrypt (Recomendado)

```bash
# Instalar certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Certbot configurará automáticamente Nginx para HTTPS
# Los certificados se renovarán automáticamente
```

## 📊 Monitoreo

### Ver logs en tiempo real

```bash
# Logs del servicio
sudo journalctl -u youtube-downloader -f

# Logs de Nginx
sudo tail -f /var/log/nginx/youtube-downloader-access.log
sudo tail -f /var/log/nginx/youtube-downloader-error.log
```

### Verificar archivos temporales

```bash
# Ver archivos en directorio temporal
ls -lh /tmp/youtube_downloads/

# Contar archivos
find /tmp/youtube_downloads -type f | wc -l
```

## 🛠️ Comandos Útiles

### Gestión del servicio

```bash
# Iniciar
sudo systemctl start youtube-downloader

# Detener
sudo systemctl stop youtube-downloader

# Reiniciar
sudo systemctl restart youtube-downloader

# Ver estado
sudo systemctl status youtube-downloader

# Ver logs
sudo journalctl -u youtube-downloader -n 50
```

### Actualizar la aplicación

```bash
# Ir al directorio
cd /var/www/youtube-downloader

# Actualizar código (si usas git)
git pull

# Activar entorno virtual
source venv/bin/activate

# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Reiniciar servicio
sudo systemctl restart youtube-downloader
```

### Limpiar manualmente archivos temporales

```bash
# Ejecutar script de limpieza
./cleanup.sh

# O manualmente
find /tmp/youtube_downloads -type f -mmin +5 -delete
```

## 🔥 Troubleshooting

### Servicio no inicia

```bash
# Ver logs detallados
sudo journalctl -u youtube-downloader -xe

# Verificar permisos
sudo chown -R www-data:www-data /var/www/youtube-downloader

# Verificar directorio temporal
sudo mkdir -p /tmp/youtube_downloads
sudo chmod 777 /tmp/youtube_downloads
```

### FFmpeg no encontrado

```bash
# Verificar instalación
ffmpeg -version

# Reinstalar si es necesario
sudo apt install --reinstall ffmpeg
```

### Puerto 5000 ocupado

```bash
# Ver qué usa el puerto
sudo lsof -i :5000

# Cambiar puerto en youtube-downloader.service
sudo nano /etc/systemd/system/youtube-downloader.service
# Cambiar --bind 0.0.0.0:5000 a otro puerto

# Recargar y reiniciar
sudo systemctl daemon-reload
sudo systemctl restart youtube-downloader
```

### Problemas de permisos

```bash
# Dar permisos correctos
sudo chown -R www-data:www-data /var/www/youtube-downloader
sudo chmod -R 755 /var/www/youtube-downloader
```

## 📈 Optimizaciones Producción

### 1. Aumentar workers de Gunicorn

```bash
# Editar servicio
sudo nano /etc/systemd/system/youtube-downloader.service

# Cambiar --workers según CPU
# Fórmula: (2 x CPU cores) + 1
# Ejemplo: 4 cores = 9 workers
```

### 2. Configurar firewall

```bash
# UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Limitar acceso por IP (opcional)

Editar [nginx.conf.example](nginx.conf.example) y agregar:

```nginx
location / {
    # Solo permitir IPs específicas
    allow 1.2.3.4;
    deny all;
    
    # ... resto de configuración
}
```

## 🎯 Checklist Final

- [ ] Sistema actualizado
- [ ] Python 3.8+ instalado
- [ ] FFmpeg instalado
- [ ] Dependencias Python instaladas
- [ ] Directorio temporal creado con permisos
- [ ] Servicio systemd configurado y corriendo
- [ ] Nginx configurado (si aplica)
- [ ] SSL configurado (si aplica)
- [ ] Cron job de limpieza activo
- [ ] Firewall configurado
- [ ] Logs funcionando correctamente

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs: `sudo journalctl -u youtube-downloader -n 100`
2. Verifica el estado: `sudo systemctl status youtube-downloader`
3. Comprueba conectividad: `curl http://localhost:5000/api/health`
4. Revisa permisos de archivos y directorios

---

**¡Listo! Tu aplicación debería estar funcionando en producción.**

Accede a: `http://tu-dominio.com` o `http://tu-ip-servidor`
