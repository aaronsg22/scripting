import os
import shutil
import datetime
import subprocess

# Rutas
web_directorio = "/var/www/html/vibst"
directorio_apache = "/etc/apache2"
directorio_local = "/server_backup"
directorio_usb = "/media/backup_disk"

# Google Drive rclone
RCLONE_REMOTE = "drivebackup"
RCLONE_FOLDER = "BackupsServidor"

# Nombre del backup con fecha y hora
fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
nombre_backup = f"backup_{fecha_hora}.tar.gz"
ruta_backup_local = os.path.join(directorio_local, nombre_backup)
ruta_backup_usb = os.path.join(directorio_usb, nombre_backup)

# Creamos una carpeta temporal para juntar todo lo que se quiere guardar
temp_dir = "/tmp/backup_temp"
os.makedirs(temp_dir, exist_ok=True)

print("Generando dumps...")

# Dump Base de Datos LDAP
subprocess.run("sudo slapcat -l {}/ldap.ldif".format(temp_dir), shell=True)

print("Copiando carpetas de la web y apache...")
shutil.copytree(web_directorio, temp_dir + "/vibst")
shutil.copytree(directorio_apache, temp_dir + "/apache2")

print("Creando archivo comprimido .tar.gz...")
shutil.make_archive(ruta_backup_local.replace('.tar.gz', ''), 'gztar', temp_dir)

print("Backup local creado en:", ruta_backup_local)

print("Copiando backup al disco externo...")
shutil.copy2(ruta_backup_local, ruta_backup_usb)

print("Subiendo backup a Google Drive con Duplicity...")
# Comando duplicity para enviar el .tar.gz a Google Drive
subprocess.run(f"duplicity {ruta_backup_local} gdocs://BackupsServidor", shell=True)

print("Backup subido a Google Drive correctamente con Duplicity.")

print("Limpiando carpeta temporal...")
shutil.rmtree(temp_dir)

print("Proceso de Backup Finalizado Correctamente.")