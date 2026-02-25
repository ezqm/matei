from flask import Flask, render_template_string, request, redirect
import sqlite3, uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "epic_og_secret_demo"

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
    c.execute("""CREATE TABLE IF NOT EXISTS cartoes (
        id TEXT PRIMARY KEY,
        produto TEXT,
        ultimos4 TEXT,
        data TEXT
    )""")

    produtos = [
        ("100 Robux", 5),
        ("1.000 Robux", 25),
        ("5.000 Robux", 120),
        ("10.000 Robux", 240),
        ("25.000 Robux", 600),
        ("50.000 Robux", 1200),
        ("100.000 Robux", 2400),
        ("150.000 Robux", 3600),
        ("200.000 Robux", 4800),
        ("250.000 Robux", 6000),
        ("300.000 Robux", 7200),
        ("350.000 Robux", 8400),
        ("400.000 Robux", 9600),
        ("450.000 Robux", 10800),
        ("500.000 Robux", 12000)
    ]
    for p in produtos:
        try:
            c.execute("INSERT INTO produtos VALUES (?,?)", p)
        except:
            pass
    conn.commit()
    conn.close()

init_db()

# ================= LOJA =================
@app.route("/", methods=["GET"])
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
:root{--bg:#eaf0f8;--card:#ffffff;--btn:#4aa5f0;--text:#000;--modal-bg:rgba(0,0,0,0.3);--modal-card:#ffffff;}
body{margin:0;background:var(--bg);font-family:Arial;color:var(--text);}
header{display:flex;justify-content:space-between;padding:20px 40px;background:#fff;box-shadow:0 2px 10px rgba(0,0,0,0.1);}
.logo{font-size:24px;font-weight:bold;color:#4aa5f0;}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;padding:30px;}
.card{background:var(--card);padding:20px;border-radius:15px;box-shadow:0 2px 10px rgba(0,0,0,0.1);text-align:center;transition:0.3s;cursor:pointer;}
.card:hover{transform:translateY(-5px);box-shadow:0 4px 20px rgba(0,0,0,0.2);}
.price{color:#4aa5f0;margin:10px 0;font-weight:bold;font-size:18px;}
.btn{padding:10px 20px;border:none;border-radius:10px;cursor:pointer;color:white;background:#4aa5f0;transition:0.3s;}
.btn:hover{opacity:0.8;}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:var(--modal-bg);justify-content:center;align-items:center;z-index:999;}
.modal.active{display:flex;}
.modal-content{background:var(--modal-card);padding:30px;border-radius:20px;width:90%;max-width:400px;text-align:center;position:relative;}
.modal-content h2{margin-top:0;color:#4aa5f0;}
.modal-content input{width:80%;padding:10px;margin:8px 0;border-radius:8px;border:1px solid #ccc;}
.modal-content .close{position:absolute;top:15px;right:15px;cursor:pointer;font-size:18px;color:#999;}
.modal-content .close:hover{color:#4aa5f0;}
</style>
</head>
<body>
<header>
<div class="logo">Epic OG Store</div>
<a href="/admin" style="color:#4aa5f0;font-weight:bold;">Admin</a>
</header>

<div class="grid">
{% for p in produtos %}
<div class="card" onclick="openModal('{{p[0]}}', {{p[1]}})">
<h3>{{p[0]}}</h3>
<div class="price">R$ {{p[1]}}</div>
<button class="btn">Comprar</button>
</div>
{% endfor %}
</div>

<div class="modal" id="modal">
<div class="modal-content">
<span class="close" onclick="closeModal()">&times;</span>
<h2 id="modal-produto">Produto</h2>
<p id="modal-valor">Valor</p>
<button class="btn" onclick="simularCartao()">💳 Cartão</button>
<button class="btn" onclick="simularPix()" style="background:#00c853">💜 Pix</button>
<div id="pagamento-area" style="margin-top:20px"></div>
</div>
</div>

<script>
function openModal(produto, valor){
document.getElementById("modal").classList.add("active");
document.getElementById("modal-produto").innerText = produto;
document.getElementById("modal-valor").innerText = "R$ "+valor;
document.getElementById("pagamento-area").innerHTML = "";
window.scrollTo(0,0);
}
function closeModal(){document.getElementById("modal").classList.remove("active");}

function simularCartao(){
document.getElementById("pagamento-area").innerHTML = `
<form onsubmit="finalizarCartao(event)">
<input id="numcartao" placeholder="Número do Cartão" required><br>
<input placeholder="Nome no Cartão" required><br>
<input placeholder="Validade" required><br>
<input placeholder="CVV" required><br><br>
<button class="btn">Pagar</button>
</form>`;
}

function simularPix(){
let codigo = "PIX-DEMO-" + Math.random().toString(36).substring(2,10).toUpperCase();
document.getElementById("pagamento-area").innerHTML = `
<p>Use o código PIX:</p>
<div style="padding:10px;background:#eee;border-radius:10px;color:#4aa5f0">${codigo}</div>
<p>⏳ Aguardando pagamento...</p>`;
setTimeout(()=>{alert("PIX simulado pago!");closeModal();},5000);
}

function finalizarCartao(e){
e.preventDefault();
let num = document.getElementById("numcartao").value;
let ult4 = num.slice(-4);

// envia via fetch para o servidor
let produto = document.getElementById("modal-produto").innerText;
fetch('/cartao_salvar', {
method:'POST',
headers:{'Content-Type':'application/x-www-form-urlencoded'},
body:'produto='+produto+'&ult4='+ult4
}).then(()=>{alert("Cartão simulado pago! Últimos 4 dígitos: " + ult4); closeModal();});
}
</script>
</body>
</html>
""", produtos=produtos)

# ================= SALVAR CARTÃO =================
@app.route("/cartao_salvar", methods=["POST"])
def cartao_salvar():
    produto = request.form['produto']
    ult4 = request.form['ult4']
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    pedido_id = str(uuid.uuid4())[:8]
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    c.execute("INSERT INTO cartoes VALUES (?,?,?,?)", (pedido_id, produto, ult4, data))
    c.execute("INSERT INTO pedidos VALUES (?,?,?,?,?,?)", (pedido_id, produto, 0, "Cartão", "Pago", data))
    conn.commit()
    conn.close()
    return "ok"

# ================= ADMIN =================
@app.route("/admin")
def admin():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM pedidos")
    pedidos = c.fetchall()
    c.execute("SELECT * FROM cartoes")
    cartoes = c.fetchall()
    conn.close()

    html = "<body style='font-family:Arial;padding:20px;background:#eaf0f8'>"
    html += "<h2>Pedidos Simulados</h2><table border=1 cellpadding=8><tr><th>ID</th><th>Produto</th><th>Valor</th><th>Método</th><th>Status</th><th>Data</th></tr>"
    for p in pedidos:
        html += f"<tr><td>{p[0]}</td><td>{p[1]}</td><td>{p[2]}</td><td>{p[3]}</td><td>{p[4]}</td><td>{p[5]}</td></tr>"
    html += "</table><br>"

    html += "<h2>Cartões Simulados</h2><table border=1 cellpadding=8><tr><th>ID</th><th>Produto</th><th>Últimos 4 dígitos</th><th>Data</th></tr>"
    for c in cartoes:
        html += f"<tr><td>{c[0]}</td><td>{c[1]}</td><td>{c[2]}</td><td>{c[3]}</td></tr>"
    html += "</table></body>"

    return html

if __name__=="__main__":
    app.run(debug=True)    box-shadow:0 0 30px rgba(157,0,255,0.2);transition:0.3s}
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
