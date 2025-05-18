
import threading
import time
import requests
import datetime
import os
import subprocess
import signal
import sys
from keep_alive import keep_alive
from flask import Flask, Response
from flask_socketio import SocketIO

# Inicializar Flask y SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Ignorar SIGHUP para evitar que procesos hijos mueran al cerrar sesión
signal.signal(signal.SIGHUP, signal.SIG_IGN)

# Último ping recibido
global last_ping
last_ping = datetime.datetime.now()

# Hilo para mantener viva la solicitud externa
def make_requests():
    while True:
        try:
            requests.get(
                'https://165c301a-f489-4cd5-bfc6-2bc5658349f0-00-227m0nhylus6k.riker.replit.dev:8080/'
            )
        except requests.RequestException:
            pass
        time.sleep(30)  # Reducido a cada 30 segundos para evitar sobrecarga

# Streaming del archivo de vídeo
def generate():
    chunk_size = 8192
    try:
        with open("rickroll.mp4", "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    except Exception as e:
        print(f"Error streaming video: {e}")

# Rutas HTTP
@app.route("/video")
def video():
    return Response(generate(), mimetype="video/mp4")

@app.route("/")
def index():
    return '''
    <video autoplay loop muted style="width:100vw;height:100vh;">
        <source src="/video" type="video/mp4">
    </video>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        var socket = io();
        setInterval(() => socket.emit('ping'), 5000);
    </script>
    '''

# WebSocket ping handler
@socketio.on('ping')
def handle_ping():
    global last_ping
    last_ping = datetime.datetime.now()
    return {'status': 'ok'}

# Hilo de verificación de conexión
def check_connection():
    global last_ping
    while True:
        if (datetime.datetime.now() - last_ping).seconds > 30:
            print("Reconectando...")
            try:
                requests.get('http://0.0.0.0:3000/')
            except requests.RequestException:
                pass
        time.sleep(10)

# Función para ejecutar stream.sh de manera segura
def run_stream():
    while True:
        try:
            # Usamos os.system en lugar de subprocess con preexec_fn
            os.system('bash stream.sh >/dev/null 2>&1')
            print("Reiniciando stream.sh...")
        except Exception as e:
            print(f"Error al ejecutar stream.sh: {e}")
        time.sleep(5)  # Esperamos 5 segundos antes de reintentar

# Hilo para crear un archivo persistente que mantenga vivo el replit
def touch_file():
    filename = ".keep_alive"
    while True:
        try:
            with open(filename, 'w') as f:
                f.write(str(datetime.datetime.now().timestamp()))
        except OSError as e:
            print(f"Error al tocar archivo: {e}")
        time.sleep(30)

# Crea un archivo .replit para configurar el comportamiento del run
def create_replit_config():
    with open(".replit", "w") as f:
        f.write('''run = "python main.py"
language = "python3"
hidden = [".config", "package-lock.json"]
persistent = true
onBoot = "bash stream.sh &"
''')

# Archivo de persistencia para replit.nix
def create_replit_nix():
    with open("replit.nix", "w") as f:
        f.write('''{ pkgs }: {
    deps = [
        pkgs.python39Packages.flask
        pkgs.python39Packages.requests
        pkgs.python39Packages.flask-socketio
    ];
}
''')

# Crear un archivo para evitar que Replit detenga el proceso
def create_keepalive_file():
    with open("keep_alive.py", "w") as f:
        f.write('''from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
''')

# Manejador de señales para cierre limpio
def signal_handler(sig, frame):
    print("Cerrando aplicación...")
    sys.exit(0)

if __name__ == "__main__":
    # Registro de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Creamos los archivos de configuración necesarios
    create_replit_config()
    create_replit_nix()
    create_keepalive_file()

    # Verificar que exista stream.sh y si no, crearlo con contenido básico
    if not os.path.exists("stream.sh"):
        with open("stream.sh", "w") as f:
            f.write('''#!/bin/bash
# Este es tu script stream.sh
# Agrega aquí el código que quieres que se ejecute persistentemente
while true; do
  echo "Stream activo: $(date)"
  sleep 60
done
''')
        os.chmod("stream.sh", 0o755)  # Hacer ejecutable el script

    # Iniciar hilos de servicio
    threads = [
        threading.Thread(target=make_requests, daemon=True),
        threading.Thread(target=check_connection, daemon=True),
        threading.Thread(target=run_stream, daemon=True),
        threading.Thread(target=touch_file, daemon=True),
    ]
    for t in threads:
        t.start()

    # Mantener la aplicación viva en Replit
    keep_alive()

    # Iniciar servidor SocketIO
    print("Servidor iniciado en http://0.0.0.0:3000")
    socketio.run(app, host="0.0.0.0", port=3000)
