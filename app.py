import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import requests

# =====================================
# CONFIGURAÇÕES INICIAIS
# =====================================
app = Flask(__name__)

# Carregar chave secreta do .env
app.secret_key = os.getenv("FLASK_SECRET_KEY", "chave_super_segura")

# Banco SQLite (local) – pode trocar depois por MySQL/Postgres
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///usuarios.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =====================================
# MODELOS DO BANCO
# =====================================
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    data_nascimento = db.Column(db.String(10), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.String(200), nullable=False)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Aguardando Pagamento")
    total = db.Column(db.Float, nullable=False)
    itens = db.relationship("ItemPedido", backref="pedido", lazy=True)

class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

# =====================================
# CRIAR BANCO
# =====================================
with app.app_context():
    db.create_all()

    # Adicionar produtos padrão (se ainda não existirem)
    if Produto.query.count() == 0:
        produtos_padrao = [
            Produto(nome="Pendrive Boot Linux", preco=40.0, imagem="linux.png"),
            Produto(nome="Pendrive Boot Android", preco=30.0, imagem="android.png"),
            Produto(nome="Pendrive Android TV", preco=35.0, imagem="androidtv.png"),
            Produto(nome="Pendrive Google TV", preco=35.0, imagem="googletv.png"),
            Produto(nome="Lista IPTV", preco=25.0, imagem="iptv.png")
        ]
        db.session.add_all(produtos_padrao)
        db.session.commit()

# =====================================
# ROTAS PRINCIPAIS
# =====================================

@app.route("/")
def index():
    produtos = Produto.query.all()
    return render_template("index.html", produtos=produtos)

# ---- Cadastro ----
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])
        cpf = request.form["cpf"]
        data_nascimento = request.form["data_nascimento"]
        endereco = request.form["endereco"]

        if Usuario.query.filter_by(email=email).first():
            flash("Email já cadastrado!", "error")
            return redirect(url_for("cadastro"))
        if Usuario.query.filter_by(cpf=cpf).first():
            flash("CPF já cadastrado!", "error")
            return redirect(url_for("cadastro"))

        novo_usuario = Usuario(
            nome=nome, email=email, senha=senha,
            cpf=cpf, data_nascimento=data_nascimento, endereco=endereco
        )
        db.session.add(novo_usuario)
        db.session.commit()

        flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for("login"))

    return render_template("cadastro.html")

# ---- Login ----
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.nome
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("index"))
        else:
            flash("Email ou senha inválidos!", "error")

    return render_template("login.html")

# ---- Logout ----
@app.route("/logout")
def logout():
    session.clear()
    flash("Logout realizado com sucesso!", "info")
    return redirect(url_for("login"))

# ---- Carrinho ----
@app.route("/add_carrinho/<int:produto_id>")
def add_carrinho(produto_id):
    if "carrinho" not in session:
        session["carrinho"] = {}

    carrinho = session["carrinho"]
    carrinho[str(produto_id)] = carrinho.get(str(produto_id), 0) + 1
    session["carrinho"] = carrinho

    flash("Produto adicionado ao carrinho!", "success")
    return redirect(url_for("index"))

@app.route("/carrinho")
def carrinho():
    if "carrinho" not in session or not session["carrinho"]:
        return render_template("carrinho.html", itens=[], total=0)

    itens = []
    total = 0
    for produto_id, quantidade in session["carrinho"].items():
        produto = Produto.query.get(int(produto_id))
        subtotal = produto.preco * quantidade
        itens.append({"produto": produto, "quantidade": quantidade, "subtotal": subtotal})
        total += subtotal

    return render_template("carrinho.html", itens=itens, total=total)

# ---- Checkout ----
@app.route("/checkout")
def checkout():
    if "usuario_id" not in session:
        flash("Faça login para finalizar a compra.", "error")
        return redirect(url_for("login"))

    carrinho = session.get("carrinho", {})
    if not carrinho:
        flash("Seu carrinho está vazio.", "error")
        return redirect(url_for("index"))

    # Calcular total
    total = 0
    for produto_id, quantidade in carrinho.items():
        produto = Produto.query.get(int(produto_id))
        total += produto.preco * quantidade

    # Criar pedido
    novo_pedido = Pedido(usuario_id=session["usuario_id"], total=total)
    db.session.add(novo_pedido)
    db.session.commit()

    for produto_id, quantidade in carrinho.items():
        produto = Produto.query.get(int(produto_id))
        item = ItemPedido(
            pedido_id=novo_pedido.id,
            produto_id=produto.id,
            quantidade=quantidade,
            subtotal=produto.preco * quantidade
        )
        db.session.add(item)
    db.session.commit()

    # Esvaziar carrinho
    session["carrinho"] = {}

    # ---- PAGAMENTO PIX ----
    pagbank_api_key = os.getenv("PAGBANK_API_KEY")
    pix_key = os.getenv("PIX_KEY", "y7172589@gmail.com")

    payload = {
        "valor": str(total),
        "chave": pix_key,
        "infoAdicionais": [{"nome": "Pedido", "valor": str(novo_pedido.id)}]
    }

    headers = {
        "Authorization": f"Bearer {pagbank_api_key}",
        "Content-Type": "application/json"
    }

    # OBS: Exemplo — chamada real depende do endpoint oficial PagBank
    # response = requests.post("https://api.pagseguro.com/pix/charges", json=payload, headers=headers)
    # link_pix = response.json().get("pixCopiaECola", "pix_gerado_aqui")

    link_pix = f"Pagamento PIX simulado para R$ {total} - Pedido #{novo_pedido.id}"

    return render_template("checkout.html", pedido=novo_pedido, link_pix=link_pix)

# ---- Meus pedidos ----
@app.route("/meus_pedidos")
def meus_pedidos():
    if "usuario_id" not in session:
        flash("Faça login para ver seus pedidos.", "error")
        return redirect(url_for("login"))

    pedidos = Pedido.query.filter_by(usuario_id=session["usuario_id"]).all()
    return render_template("meus_pedidos.html", pedidos=pedidos)

# ---- Admin (pedidos) ----
@app.route("/admin/pedidos")
def admin_pedidos():
    pedidos = Pedido.query.all()
    return render_template("admin_pedidos.html", pedidos=pedidos)

# =====================================
# RODAR SERVIDOR
# =====================================
if __name__ == "__main__":
    app.run(debug=True)
