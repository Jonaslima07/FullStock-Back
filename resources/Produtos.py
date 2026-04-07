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


# LISTAR PRODUTOS
@produtos_bp.route("/produtos", methods=["GET"])
@jwt_required()
def listar_produtos():

    user_id = int(get_jwt_identity())

    usuario = db.session.get(Usuario, user_id)

    if not usuario:
        return jsonify({"msg": "Usuário não encontrado"}), 404

    if not usuario.comercio:
        return jsonify({"msg": "Usuário sem comércio"}), 400

    page = request.args.get("page", 1, type=int)
    per_page = 50

    if per_page > 100:
        per_page = 100

    produtos = Produto.query.filter_by(
        comercio_id=usuario.comercio.id
    ).paginate(page=page, per_page=per_page)

    return jsonify({
        "produtos": produtos_schema.dump(produtos.items),
        "total": produtos.total,
        "pages": produtos.pages,
        "page": produtos.page
    }), 200

# CRIAR PRODUTO
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
        unidade=dados["unidade"],
        data_validade=dados["data_validade"],
        comercio_id=usuario.comercio.id
    )

    db.session.add(produto)
    db.session.commit()

    return jsonify(produto_schema.dump(produto)), 201


# ATUALIZAR PRODUTO
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

    for campo, valor in dados.items():
        setattr(produto, campo, valor)

    db.session.commit()

    return jsonify(produto_schema.dump(produto)), 200


# DELETAR PRODUTO
@produtos_bp.route("/produtos/<int:id>", methods=["DELETE"])
@jwt_required()
def deletar_produto(id):

    produto = db.session.get(Produto, id)

    if not produto:
        return jsonify({"error": "Produto não encontrado"}), 404

    db.session.delete(produto)
    db.session.commit()

    return jsonify({"message": "Produto removido com sucesso"}), 200