from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = "chave-secreta-supr-segura"

def init_db():
    conn = sqlite3.connect("mensagens.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            mensagem TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


@app.route("/contato", methods=["GET", "POST"])
def contato():
    if request.method == "POST":
        nome = request.form["nome"]
        mensagem = request.form["mensagem"]

        conn = sqlite3.connect("mensagens.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO mensagens (nome, mensagem) VALUES (?, ?)", (nome, mensagem))
        conn.commit()
        conn.close()

        flash("Mensagem enviada com sucesso! ✅")
        return redirect(url_for("contato"))
    
    return render_template("contato.html")

#Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        #Login e senha
        if usuario == "admin" and senha == "Samurai100%":
            session["logado"] = True
            flash("Login realizado com sucesso!")
            return redirect(url_for("listar_mensagens"))
        else:
            flash("Usário ou senha incorretos")
    return render_template("login.html")

#Logout
@app.route("/logout")
def logout():
    session.pop("logado", None)
    flash("Você saiu da sessão")
    return redirect(url_for("login"))



#Listar mensagens
@app.route("/mensagens")
def listar_mensagens():
    if not session.get("logado"):
        flash("Você precisa fazer login para acessar esta página")
        return redirect(url_for("login"))

    conn = sqlite3.connect("mensagens.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, mensagem FROM mensagens ORDER BY id DESC")
    mensagens = cursor.fetchall()
    conn.close()
    return render_template("mensagens.html", mensagens=mensagens)
if __name__ == "__main__":
    init_db()
    app.run(debug=True)