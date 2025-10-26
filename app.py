from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, send
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"  # altere para algo seguro
socketio = SocketIO(app, cors_allowed_origins="*")

# Lista de usuários conectados
usuarios_conectados = set()

# Fuso horário de Brasília
brasilia = pytz.timezone('America/Sao_Paulo')

# Página de login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        if usuario:
            session["usuario"] = usuario
            return redirect(url_for("chat"))
    return render_template("login.html")

# Página do chat
@app.route("/chat")
def chat():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("chat.html", usuario=session["usuario"])

# Conexão de usuário
@socketio.on('connect')
def handle_connect(auth=None):
    usuario = session.get('usuario', 'Anônimo')
    usuarios_conectados.add(usuario)
    send(f"🔵 {usuario} entrou no chat!")
    socketio.emit('user_count', len(usuarios_conectados))

# Desconexão de usuário
@socketio.on('disconnect')
def handle_disconnect():
    usuario = session.get('usuario', 'Anônimo')
    usuarios_conectados.discard(usuario)
    send(f"🔴 {usuario} saiu do chat!")
    socketio.emit('user_count', len(usuarios_conectados))

# Receber mensagem do cliente
@socketio.on('mensagem')
def handle_mensagem(msg):
    usuario = session.get('usuario', 'Anônimo')
    # Hora com fuso de Brasília
    hora = datetime.now(brasilia).strftime("%H:%M")
    texto = f"{usuario} ({hora}): {msg}"
    send(texto)

if __name__ == "__main__":
    # Para testes locais
    socketio.run(app, host="0.0.0.0", port=5000)
