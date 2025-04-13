import psutil
import datetime
from colorama import Fore, Style, init
from crontab import CronTab

# Inicialización de colorama para usar colores en la terminal
init(autoreset=True)

# ===========================
# FUNCIONES PARA OBTENER DATOS
# ===========================

def uso_de_cpu():
    """Obtiene el porcentaje de uso de la CPU."""
    return psutil.cpu_percent(interval=1)

def uso_de_memoria():
    """Obtiene el porcentaje de uso de la memoria RAM."""
    return psutil.virtual_memory().percent

def espacio_del_disco():
    """Obtiene el porcentaje de espacio utilizado en el disco duro."""
    return psutil.disk_usage('/').percent

def tiempo_encendido():
    """Obtiene el tiempo que ha estado encendido el sistema."""
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    tiempo_encendido = datetime.datetime.now() - boot_time
    dias = tiempo_encendido.days
    horas, resto = divmod(tiempo_encendido.seconds, 3600)
    minutos, _ = divmod(resto, 60)
    return f"{dias} días, {horas}h {minutos}min"

def uso_cpu_por_nucleo():
    """Obtiene el uso de CPU por cada núcleo."""
    return psutil.cpu_percent(interval=1, percpu=True)

def temperatura_sensores():
    """Obtiene las temperaturas de los sensores del sistema, si están disponibles."""
    try:
        temperaturas = psutil.sensors_temperatures()['coretemp'][0].current
        return f"Temperatura del CPU: {temperaturas} ºC"
    except Exception as e:
        return f"Error al obtener temperatura: {e}"

def procesos_cpu():
    """Obtiene una lista de los primeros procesos más intensivos en CPU."""
    procesos = [(p.info['pid'], p.info['name'], p.info['cpu_percent'])
                for p in psutil.process_iter(['pid', 'name', 'cpu_percent'])]
    procesos_ordenados = sorted(procesos, key=lambda x: x[2], reverse=True)
    return procesos_ordenados[:5]  # Top 5 procesos con mayor uso de CPU

# ===========================
# FUNCION PARA CREAR EL LOG
# ===========================

def crear_log(mensaje):
    """Crea un log con los datos proporcionados."""
    with open('monitor_servidor.log', 'a') as archivo:
        archivo.write(f"{datetime.datetime.now()}: {mensaje}\n")

# ===========================
# FUNCIONES DE IMPRESIÓN
# ===========================

def imprimir_datos():
    """Muestra los datos en la terminal con colores."""
    uso_cpu_valor = uso_de_cpu()
    uso_memoria_valor = uso_de_memoria()
    uso_disco_valor = espacio_del_disco()
    tiempo_encendido_valor = tiempo_encendido()
    cpu_por_nucleo_valor = uso_cpu_por_nucleo()
    temperatura_valor = temperatura_sensores()
    top_procesos = procesos_cpu()

    # Añadir un diseño más bonito a la impresión
    print(Fore.LIGHTCYAN_EX + "="*50)
    print(Fore.YELLOW + "         MONITOR DE RENDIMIENTO DEL SISTEMA")
    print(Fore.LIGHTCYAN_EX + "="*50)

    print(Fore.GREEN + f"\n{Style.BRIGHT}↳ Uso de CPU: {uso_cpu_valor}%")
    print(Fore.CYAN + f"↳ Uso de memoria RAM: {uso_memoria_valor}%")
    print(Fore.MAGENTA + f"↳ Espacio usado en el disco: {uso_disco_valor}%")
    print(Fore.RED + f"↳ Tiempo encendido: {tiempo_encendido_valor}")
    print(Fore.YELLOW + f"↳ Uso de CPU por núcleo: {cpu_por_nucleo_valor}")
    print(Fore.BLUE + f"↳ Temperatura del CPU: {temperatura_valor}")

    print(Fore.LIGHTYELLOW_EX + "\nTop 5 procesos con mayor uso de CPU:")
    for pid, name, cpu in top_procesos:
        print(f"{Fore.LIGHTGREEN_EX}PID: {pid} {Style.BRIGHT}Nombre: {name} - Uso CPU: {cpu}%")

    print(Fore.LIGHTCYAN_EX + "="*50)

    # Crear log con toda la información
    info_log = (
        f"Uso de CPU: {uso_cpu_valor}%\n"
        f"Uso de memoria RAM: {uso_memoria_valor}%\n"
        f"Espacio usado en el disco: {uso_disco_valor}%\n"
        f"Tiempo encendido: {tiempo_encendido_valor}\n"
        f"Uso de CPU por núcleo: {cpu_por_nucleo_valor}\n"
        f"Temperatura del CPU: {temperatura_valor}\n"
        f"Top 5 procesos de CPU: {top_procesos}"
    )
    crear_log(info_log)

# ===========================
# EJECUCIÓN PRINCIPAL
# ===========================

if __name__ == "__main__":
    imprimir_datos()

cron = CronTab(user=True)  # Crea un crontab per l'usuari actual
job = cron.new(command='python3 /home/isard/scripting/monitorización.py', comment='Monitor monitorización.py')
job.minute.every(5)  # Programa l'script cada 5 minuts

cron.write()  # Desa la configuració
print("Tasca programada!")
