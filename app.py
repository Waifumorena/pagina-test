import threading
import asyncio
import websockets
import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

# Conexión a la base de datos SQLite
conn = sqlite3.connect('waifusmo_Emy.db')
c = conn.cursor()

# Crear la tabla mensajes si no existe
c.execute('''CREATE TABLE IF NOT EXISTS mensajes
             (mensaje text)''')

# Crear un Lock para proteger el acceso a la base de datos SQLite
lock = threading.Lock()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            return render_template('admin.html')
        elif username == 'empleado' and password == 'empleado':
            return render_template('empleado.html')
        else:
            error = 'Credenciales inválidas. Intente de nuevo.'
    return render_template('login.html', error=error)


# Dirección IP del servidor
HOST = '149.56.67.133'
# Puerto en el que se ejecutará el servidor
PORT = 5001

# Lista de clientes conectados al servidor
clientes = set()

async def manejar_cliente(websocket, path):
    # Agregar el cliente a la lista de clientes
    clientes.add(websocket)

    # Manejar los mensajes del cliente
    async for mensaje in websocket:
        # Enviar el mensaje a todos los clientes conectados
        for cliente in clientes:
            await cliente.send(mensaje)

        # Guardar el mensaje en la base de datos SQLite
        with lock:
            c.execute("INSERT INTO mensajes (mensaje) VALUES (?)", (mensaje,))
            conn.commit()

    # Eliminar el cliente de la lista de clientes
    clientes.remove(websocket)

# Iniciar el servidor WebSocket
async def iniciar_servidor():
    async with websockets.serve(manejar_cliente, HOST, PORT):
        print(f"Servidor escuchando en {HOST}:{PORT}...")
        await asyncio.Future()  # Mantener el servidor en funcionamiento indefinidamente

if __name__ == '__main__':
    # Obtener el bucle de eventos de asyncio actual
    loop = asyncio.get_event_loop()

    # Crear tareas para el servidor Flask y el servidor WebSocket
    tarea_flask = threading.Thread(target=app.run, kwargs={'host': '149.56.67.133', 'port': 5000})
    tarea_websockets = threading.Thread(target=loop.run_until_complete, args=(iniciar_servidor(),))

    # Iniciar las tareas en hilos separados
    tarea_flask.start()
    tarea_websockets.start()

    # Esperar a que las tareas finalicen
    tarea_flask.join()
    tarea_websockets.join()

    # Cerrar la conexión a la base de datos SQLite
    conn.close()







