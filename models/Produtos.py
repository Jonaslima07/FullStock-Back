from helpers.database import db

class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50))
    quantidade = db.Column(db.Integer, default=0)
    tipo = db.Column(db.String(50), nullable=True)
    preco = db.Column(db.Float)
    marca = db.Column(db.String(100), nullable=True)
    unidade = db.Column(db.String(50), nullable=True)
    data_validade = db.Column(db.Date, nullable=False)
    comercio_id = db.Column(db.Integer,db.ForeignKey("comercios.id"),nullable=False,index=True)

    def __repr__(self):
        return f"<Produto {self.nome}>"
