import eventlet
eventlet.monkey_patch()  # 👈 precisa vir antes de qualquer import Flask

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta, timezone

# Fuso horário do Brasil (UTC-3)
BRASIL_TZ = timezone(timedelta(hours=-3))

app = Flask(__name__)
app.secret_key = "chave-secreta"
socketio = SocketIO(app, async_mode='eventlet')

usuarios_conectados = set()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        if usuario:
            session["usuario"] = usuario
            return redirect(url_for("chat"))
    return render_template("login.html")

@app.route("/chat")
def chat():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("login"))
    return render_template("chat.html", usuario=usuario)

@socketio.on("connect")
def handle_connect(auth=None):
    usuario = session.get("usuario", "Anônimo")
    usuarios_conectados.add(usuario)

    # Envia mensagem global
    hora = datetime.now(BRASIL_TZ).strftime("%H:%M:%S")
    socketio.emit("message", f"[{hora}] 🔵 {usuario} entrou no chat.")
    socketio.emit("user_count", len(usuarios_conectados), to=None)  # para todos

@socketio.on("disconnect")
def handle_disconnect():
    usuario = session.get("usuario", "Anônimo")
    if usuario in usuarios_conectados:
        usuarios_conectados.remove(usuario)

    hora = datetime.now(BRASIL_TZ).strftime("%H:%M:%S")
    socketio.emit("message", f"[{hora}] 🔴 {usuario} saiu do chat.")
    socketio.emit("user_count", len(usuarios_conectados), to=None)

@socketio.on("mensagem")
def handle_message(msg):
    usuario = session.get("usuario", "Anônimo")
    hora = datetime.now(BRASIL_TZ).strftime("%H:%M:%S")
    texto = f"[{hora}] 💬 {usuario}: {msg}"
    
    # Envia mensagem para todos os usuários
    socketio.emit("message", texto, to=None)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
