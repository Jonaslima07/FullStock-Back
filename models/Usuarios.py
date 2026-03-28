from helpers.database import db

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(
        db.String(120),
        unique=True,
        index=True,  # 👈 cria índice no banco
        nullable=False
    )
    photo = db.Column(db.String(255))
    cpf = db.Column(db.String(11), nullable=True)
    senha = db.Column(db.String(255), nullable=True)
    cadastro_completo = db.Column(db.Boolean, default=False)

    comercio = db.relationship(
        "Comercio",
        backref="usuario",
        uselist=False,
        lazy="joined"  # 👈 evita query extra quando buscar usuário
    )