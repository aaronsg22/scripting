import os
import subprocess
from datetime import datetime

# Rutas
DIRECTORIOS_A_COPIAR = ["/var/www", "/etc/apache2", "/var/lib/ldap"]  
RUTA_DESTINO_LOCAL = "/server_backup"
RUTA_DESTINO_DISCO_EXTERNO = "/mnt/disc_extern/server_backup"
RCLONE_REMOTO = "drive_backup:server_backup"  # Hay que editarlo una vez pongamos rclone
# Comprobar que las rutas existan o las crea
for ruta in [RUTA_DESTINO_LOCAL, RUTA_DESTINO_DISCO_EXTERNO]:
    os.makedirs(ruta, exist_ok=True)

def hacer_backup_duplicity(origen, destino):
    """
    Hace una copia incremental con duplicity.
    """
    try:
        print(f"Iniciando copia incremental de {origen} a {destino}...")
        subprocess.run(["duplicity", origen, destino], check=True)
        print(f"Copia completada: {destino}")
    except subprocess.CalledProcessError as e:
        print(f"Error al hacer la copia: {e}")

def duplicar_backup_local():
    """
    Duplica el contenido de /server_backup al disco externo.
    """
    try:
        print(f"Copiando {RUTA_DESTINO_LOCAL} a {RUTA_DESTINO_DISCO_EXTERNO}...")
        subprocess.run(["rsync", "-a", RUTA_DESTINO_LOCAL + "/", RUTA_DESTINO_DISCO_EXTERNO + "/"], check=True)
        print("Copia al disco externo completada.")
    except subprocess.CalledProcessError as e:
        print(f"Error copiando al disco externo: {e}")

def subir_a_nube():
    """
    Utiliza rclone para subir a la nube.
    """
    try:
        print("Subiendo la copia a la nube...")
        subprocess.run(["rclone", "sync", RUTA_DESTINO_LOCAL, RCLONE_REMOTO], check=True)
        print("Copia a la nube completada.")
    except subprocess.CalledProcessError as e:
        print(f"Error subiendo a la nube: {e}")

def main():
    # Combina todos los directorios de origen en uno solo temporal para hacer la copia. 
    # En esta parte del codigo nos hemos ayudado de inteligencia artifial para hacerlo ya que no sabiamos como hacerlo. 
    directorio_temporal = "/tmp/backup_temp"
    os.makedirs(directorio_temporal, exist_ok=True)

    print("Copiando directorios a un directorio temporal...")
    for origen in DIRECTORIOS_A_COPIAR:
        nombre = os.path.basename(origen.rstrip('/'))
        destino = os.path.join(directorio_temporal, nombre)
        subprocess.run(["rsync", "-a", origen + "/", destino + "/"], check=True)

    # Hacer backup incremental con duplicity
    hacer_backup_duplicity(directorio_temporal, f"file://{RUTA_DESTINO_LOCAL}")

    # Duplica localmente
    duplicar_backup_local()

    # Sube a la nube
    subir_a_nube()

    # Limpieza
    subprocess.run(["rm", "-rf", directorio_temporal])

if __name__ == "__main__":
    main()
