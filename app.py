from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, send, join_room, leave_room
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'segredo123')
socketio = SocketIO(app, cors_allowed_origins="*")

usuarios_conectados = set()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form.get('nome')
        if nome:
            session['usuario'] = nome
            usuarios_conectados.add(nome)
            return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/chat')
def chat():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', usuario=session['usuario'], count=len(usuarios_conectados))

@socketio.on('connect')
def handle_connect():
    usuario = session.get('usuario', 'Anônimo')
    if usuario not in usuarios_conectados:
        usuarios_conectados.add(usuario)
    send(f"🔵 {usuario} entrou no chat!", broadcast=True)
    socketio.emit('user_count', len(usuarios_conectados), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    usuario = session.get('usuario', 'Anônimo')
    usuarios_conectados.discard(usuario)
    send(f"🔴 {usuario} saiu do chat!", broadcast=True)
    socketio.emit('user_count', len(usuarios_conectados), broadcast=True)

@socketio.on('message')
def handle_message(msg):
    usuario = session.get('usuario', 'Anônimo')
    hora = datetime.now().strftime("%H:%M")
    texto = f"{usuario} ({hora}): {msg}"
    send(texto, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
