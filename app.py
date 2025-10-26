from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, send
import os

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
    return render_template('chat.html', usuario=session['usuario'])

@socketio.on('message')
def handle_message(msg):
    usuario = session.get('usuario', 'Anônimo')
    texto = f"{usuario}: {msg}"
    send(texto, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
