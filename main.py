import subprocess
import time
import sys
import os

def install_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ FFmpeg ya está instalado.")
    except FileNotFoundError:
        print("⏳ Instalando FFmpeg...")
        if sys.platform.startswith("linux"):
            subprocess.run(["sudo", "apt", "update", "-y"])
            subprocess.run(["sudo", "apt", "install", "ffmpeg", "-y"])
        elif sys.platform == "darwin":
            subprocess.run(["brew", "install", "ffmpeg"])
        elif sys.platform.startswith("win"):
            print("⚠️ En Windows, instala FFmpeg manualmente o agrega su ruta al PATH.")
        else:
            print("❌ Sistema operativo no soportado para instalación automática.")

def stream_loop():
    YT_KEY = "wv5f-kxt7-aars-mr7e-byht"
    VIDEO_INPUT = "https://165c301a-f489-4cd5-bfc6-2bc5658349f0-00-227m0nhylus6k.riker.replit.dev/video"

    ffmpeg_command = [
        "ffmpeg",
        "-re",
        "-stream_loop", "-1",
        "-i", VIDEO_INPUT,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-maxrate", "2000k",
        "-bufsize", "4000k",
        "-g", "30",
        "-r", "24",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-f", "flv",
        f"rtmp://a.rtmp.youtube.com/live2/{YT_KEY}"
    ]

    while True:
        try:
            print("📡 Iniciando transmisión Rickroll en bucle...")
            subprocess.run(ffmpeg_command)
            print("💤 FFmpeg finalizó. Reiniciando en 2 segundos...")
            time.sleep(2)
        except KeyboardInterrupt:
            print("🛑 Transmisión detenida por el usuario.")
            break
        except Exception as e:
            print(f"💥 Error inesperado: {e}")
            time.sleep(2)

if __name__ == "__main__":
    install_ffmpeg()
    stream_loop()
