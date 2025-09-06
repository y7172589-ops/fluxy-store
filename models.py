"""
models.py

Define os modelos/tabelas do banco de dados para a Fluxy Store.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Instância global do SQLAlchemy (inicializada no app.py)
db = SQLAlchemy()

# ------------------------------
# Modelo de Usuário
# ------------------------------
class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    data_nascimento = db.Column(db.String(10), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    pedidos = db.relationship("Pedido", back_populates="usuario", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Usuario {self.email}>"

# ------------------------------
# Modelo de Produto
# ------------------------------
class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.String(200), nullable=True)  # caminho para a imagem
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    itens = db.relationship("ItemPedido", back_populates="produto")

    def __repr__(self):
        return f"<Produto {self.nome} R${self.preco}>"

# ------------------------------
# Modelo de Pedido
# ------------------------------
class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    status = db.Column(db.String(50), default="Pendente")  # Pendente, Pago, Enviado, Entregue
    total = db.Column(db.Float, default=0.0)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship("Usuario", back_populates="pedidos")
    itens = db.relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")

    def calcular_total(self):
        self.total = sum(item.subtotal for item in self.itens)
        return self.total

    def __repr__(self):
        return f"<Pedido {self.id} - Usuario {self.usuario_id} - Total {self.total}>"

# ------------------------------
# Modelo de ItemPedido (N:N entre Pedido e Produto)
# ------------------------------
class ItemPedido(db.Model):
    __tablename__ = "itens_pedido"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)
    quantidade = db.Column(db.Integer, default=1)
    preco_unitario = db.Column(db.Float, nullable=False)

    pedido = db.relationship("Pedido", back_populates="itens")
    produto = db.relationship("Produto", back_populates="itens")

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def __repr__(self):
        return f"<ItemPedido Pedido {self.pedido_id} Produto {self.produto_id}>"
