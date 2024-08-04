import random
import requests
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

# Configuración de la conexión a la base de datos
DATABASE_CONFIG = {
    'host': 'monorail.proxy.rlwy.net',
    'port': '33906',
    'user': 'root',
    'password': 'TmtzzQJRSKPjmBeCWDBPyPtJbUfTzRQv',
    'database': 'reservas'
}

try:
    conn = mysql.connector.connect(**DATABASE_CONFIG)
    if conn.is_connected():
        print("Conexión exitosa a la base de datos")
except Error as e:
    print(f"Error al conectar a la base de datos: {e}")
    exit()

def obtener_usuarios():
    try:
        response = requests.get('https://randomuser.me/api/?results=10')
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
        data = response.json()
        return data['results']
    except requests.RequestException as e:
        print(f"Error al obtener usuarios: {e}")
        return []

def agregar_reserva():
    cursor = conn.cursor()
    usuarios = obtener_usuarios()
    for user in usuarios:
        nombre = user['name']['first']
        apellido = user['name']['last']
        email = user['email']
        telefono = user['phone']

        try:
            # Insertar nuevo cliente en la base de datos y obtener su ID
            cursor.execute("INSERT INTO clientes (nombre, apellido, email, telefono) VALUES (%s, %s, %s, %s)",
                           (nombre, apellido, email, telefono))
            cliente_id = cursor.lastrowid

            # Seleccionar una mesa al azar
            cursor.execute("SELECT mesa_id FROM mesas ORDER BY RAND() LIMIT 1")
            mesa_id = cursor.fetchone()[0]

            # Generar fecha y hora para la reserva
            fecha = datetime.now().date() + timedelta(days=random.randint(1, 30))
            hora = (datetime.now() + timedelta(minutes=random.randint(0, 1440))).time()

            # Insertar nueva reserva en la base de datos
            cursor.execute("INSERT INTO reservas (cliente_id, mesa_id, fecha, hora, estado) VALUES (%s, %s, %s, %s, %s)",
                           (cliente_id, mesa_id, fecha, hora, "pendiente"))

            # Confirmar los cambios
            conn.commit()
        except Error as e:
            print(f"Error al agregar reserva: {e}")
            conn.rollback()  # Deshacer cambios en caso de error

    cursor.close()

if __name__ == "__main__":
    agregar_reserva()
    conn.close()
