from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from models.Produtos import Produto
from models.Usuarios import Usuario
from schema.produtos_schema import ProdutoSchema
from helpers.database import db

produtos_bp = Blueprint("produtos", __name__)

produto_schema = ProdutoSchema()
produtos_schema = ProdutoSchema(many=True)



@produtos_bp.route("/produtos", methods=["GET"])
@jwt_required()
def listar_produtos():

    user_id = int(get_jwt_identity())

    usuario = db.session.get(Usuario, user_id)

    if not usuario:
        return jsonify({"msg": "Usuário não encontrado"}), 404

  

    produtos = Produto.query.filter_by(
        comercio_id=usuario.comercio.id
    ).all()
    
    lista = []

    for p in produtos:
        lista.append({
            "id": p.id,
            "nome": p.nome,
            "marca": p.marca,
            "tipo": p.tipo,
            "categoria": p.categoria,
            "quantidade": p.quantidade,
            "preco": p.preco,
            "unidade": p.unidade,
            "data_validade": str(p.data_validade)
        })

    return jsonify(lista), 200

@produtos_bp.route("/produtos", methods=["POST"])
@jwt_required()
def criar_produto():

    try:
        dados = produto_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user_id = int(get_jwt_identity())
    usuario = db.session.get(Usuario, user_id)

    if not usuario:
        return jsonify({"msg": "Usuário não encontrado"}), 404

    if not usuario.comercio:
        return jsonify({"msg": "Usuário sem comércio"}), 400

    produto = Produto(
        nome=dados["nome"],
        categoria=dados["categoria"],
        quantidade=dados["quantidade"],
        preco=dados["preco"],
        marca=dados["marca"],
        tipo=dados["tipo"],
        unidade=dados["unidade"],
        data_validade=dados["data_validade"],
        comercio_id=usuario.comercio.id
    )

    db.session.add(produto)
    db.session.commit()

    return jsonify(produto_schema.dump(produto)), 201



@produtos_bp.route("/produtos/<int:id>", methods=["PUT"])
@jwt_required()
def atualizar_produtos(id):

    produto = db.session.get(Produto, id)

    if not produto:
        return jsonify({"msg": "Produto não encontrado"}), 404

    try:
        dados = produto_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    if "nome" in dados:
        produto.nome = dados["nome"]

    if "categoria" in dados:
        produto.categoria = dados["categoria"]

    if "quantidade" in dados:
        produto.quantidade = dados["quantidade"]

    if "preco" in dados:
        produto.preco = dados["preco"]

    if "marca" in dados:
        produto.marca = dados["marca"]

    if "tipo" in dados:
        produto.tipo = dados["tipo"]

    if "unidade" in dados:
        produto.unidade = dados["unidade"]
    
    if "data_validade" in dados:
        produto.data_validade = dados["data_validade"]

    db.session.commit()

    return jsonify(produto_schema.dump(produto)), 200



@produtos_bp.route("/produtos/<int:id>", methods=["DELETE"])
@jwt_required()
def deletar_produto(id):

    produto = db.session.get(Produto, id)

    if not produto:
        return jsonify({"error": "Produto não encontrado"}), 404

    db.session.delete(produto)
    db.session.commit()

    return jsonify({"message": "Produto removido com sucesso"}), 200