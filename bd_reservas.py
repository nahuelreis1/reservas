import random
import requests
import mysql.connector
from datetime import datetime, timedelta

# Configuración de la conexión a la base de datos
DATABASE_CONFIG = {
    'host': 'roundhouse.proxy.rlwy.net',
    'user': 'root',
    'password': 'RHjfeSJbGjmLkcotvMaehaTtgBogMgMs',
    'database': 'reservas'
}

conn = mysql.connector.connect(**DATABASE_CONFIG)

def obtener_usuarios():
    response = requests.get('https://randomuser.me/api/?results=10')
    data = response.json()
    return data['results']

def agregar_reserva():
    cursor = conn.cursor()
    usuarios = obtener_usuarios()

    for user in usuarios:
        nombre = user['name']['first']
        apellido = user['name']['last']
        email = user['email']
        telefono = user['phone']

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
    cursor.close()

if __name__ == "__main__":
    agregar_reserva()
    conn.close()

