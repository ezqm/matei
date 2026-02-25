from flask import Flask, request, render_template_string, redirect, session
import sqlite3, uuid, base64, time
import qrcode
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
app.secret_key = "epic_og_admin_secret"

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS produtos (
        nome TEXT PRIMARY KEY,
        valor REAL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS pedidos (
        id TEXT PRIMARY KEY,
        produto TEXT,
        valor REAL,
        metodo TEXT,
        status TEXT,
        data TEXT
    )""")

    base = [
        ("100 Robux", 5),
        ("1.000 Robux", 25),
        ("10.000 Robux", 120),
        ("100.000 Robux", 500),
        ("700.000 Robux", 2500),
    ]

    for p in base:
        try:
            c.execute("INSERT INTO produtos VALUES (?,?)", p)
        except:
            pass

    conn.commit()
    conn.close()

init_db()

# ================= LOJA =================
@app.route("/")
def loja():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM produtos")
    produtos = c.fetchall()
    conn.close()

    return render_template_string("""
    <html>
    <head>
    <title>Epic OG Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body{margin:0;background:#0f0f12;color:white;font-family:Arial}
    header{display:flex;justify-content:space-between;padding:20px 40px;background:#111}
    .logo{color:#9d00ff;font-size:22px;font-weight:bold}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:25px;padding:40px}
    .card{background:#1a1a1f;padding:25px;border-radius:20px;text-align:center;
    box-shadow:0 0 30px rgba(157,0,255,0.2);transition:0.3s}
    .card:hover{transform:translateY(-5px);box-shadow:0 0 40px rgba(157,0,255,0.6)}
    .btn{padding:10px 20px;border:none;border-radius:12px;cursor:pointer;margin:5px}
    .card-btn{background:#9d00ff;color:white}
    .pix-btn{background:#00c853;color:white}
    a{text-decoration:none}
    </style>
    </head>
    <body>
    <header>
        <div class="logo">⚡ Epic OG Store</div>
        <a href="/admin" style="color:white">Admin</a>
    </header>
    <div class="grid">
    {% for p in produtos %}
    <div class="card">
        <h2>{{p[0]}}</h2>
        <p style="color:#9d00ff">R$ {{p[1]}}</p>
        <a href="/cartao/{{p[0]}}"><button class="btn card-btn">💳 Cartão</button></a>
        <a href="/pix/{{p[0]}}"><button class="btn pix-btn">💜 Pix</button></a>
    </div>
    {% endfor %}
    </div>
    </body>
    </html>
    """, produtos=produtos)

# ================= CARTAO DEMO =================
@app.route("/cartao/<produto>", methods=["GET","POST"])
def cartao(produto):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT valor FROM produtos WHERE nome=?", (produto,))
    valor = c.fetchone()[0]

    if request.method == "POST":
        pedido_id = str(uuid.uuid4())[:8]
        data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        c.execute("INSERT INTO pedidos VALUES (?,?,?,?,?,?)",
                  (pedido_id, produto, valor, "Cartão", "Pago", data))
        conn.commit()
        conn.close()
        return redirect(f"/sucesso/{pedido_id}")

    conn.close()
    return f"""
    <body style="background:#0f0f12;color:white;font-family:Arial;text-align:center;padding:50px">
    <h2>💳 Cartão - DEMO</h2>
    <h3>{produto}</h3>
    <form method="post">
    <input placeholder="Número do Cartão" required><br><br>
    <input placeholder="Nome no Cartão" required><br><br>
    <input placeholder="Validade" required><br><br>
    <input placeholder="CVV" required><br><br>
    <button style="padding:10px 20px;background:#9d00ff;border:none;border-radius:10px;color:white">Pagar</button>
    </form>
    <p style="color:red;margin-top:20px;">⚠️ Pagamento Simulado</p>
    </body>
    """

# ================= PIX DEMO =================
@app.route("/pix/<produto>")
def pix(produto):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT valor FROM produtos WHERE nome=?", (produto,))
    valor = c.fetchone()[0]

    pedido_id = str(uuid.uuid4())[:8]
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    c.execute("INSERT INTO pedidos VALUES (?,?,?,?,?,?)",
              (pedido_id, produto, valor, "Pix", "Aguardando", data))
    conn.commit()
    conn.close()

    codigo_pix = f"PIX-DEMO-{pedido_id}"
    qr = qrcode.make(codigo_pix)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"""
    <body style="background:#0f0f12;color:white;font-family:Arial;text-align:center;padding:30px">
    <h2>💜 PIX - DEMO</h2>
    <img src="data:image/png;base64,{img_str}" width="250"><br><br>
    <p>{codigo_pix}</p>
    <p>⏳ Aguardando pagamento...</p>
    <script>
    setTimeout(function(){{
        window.location.href="/confirmar/{pedido_id}";
    }}, 8000);
    </script>
    <p style="color:red;">⚠️ Pagamento Simulado</p>
    </body>
    """

@app.route("/confirmar/<pedido_id>")
def confirmar(pedido_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("UPDATE pedidos SET status='Pago' WHERE id=?", (pedido_id,))
    conn.commit()
    conn.close()
    return redirect(f"/sucesso/{pedido_id}")

# ================= SUCESSO =================
@app.route("/sucesso/<pedido_id>")
def sucesso(pedido_id):
    return f"""
    <body style="background:#0f0f12;color:white;font-family:Arial;text-align:center;margin-top:150px">
    <h1>✅ Pagamento Confirmado</h1>
    <h3>ID: {pedido_id}</h3>
    <a href="/" style="color:#9d00ff;">Voltar</a>
    </body>
    """

# ================= ADMIN =================
@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form["user"] == "admin" and request.form["senha"] == "1234":
            session["admin"] = True

    if not session.get("admin"):
        return """
        <body style="background:#0f0f12;color:white;font-family:Arial;text-align:center;padding:50px">
        <h2>Login Admin</h2>
        <form method="post">
        <input name="user" placeholder="Usuário"><br><br>
        <input name="senha" placeholder="Senha" type="password"><br><br>
        <button>Entrar</button>
        </form>
        </body>
        """

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM pedidos")
    pedidos = c.fetchall()

    total = sum([p[2] for p in pedidos])

    html = """
    <body style="background:#0f0f12;color:white;font-family:Arial;padding:40px">
    <h1>📊 Painel Admin</h1>
    <h3>Total de Vendas (Simulado): R$ """ + str(total) + """</h3>
    <table border="1" cellpadding="10">
    <tr>
    <th>ID</th><th>Produto</th><th>Valor</th><th>Método</th><th>Status</th><th>Data</th>
    </tr>
    """

    for p in pedidos:
        html += f"<tr><td>{p[0]}</td><td>{p[1]}</td><td>{p[2]}</td><td>{p[3]}</td><td>{p[4]}</td><td>{p[5]}</td></tr>"

    html += "</table><br><a href='/'>Voltar</a></body>"

    conn.close()
    return html

if __name__ == "__main__":
    app.run()
