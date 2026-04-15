import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from marshmallow import ValidationError
from extensions.limiter import limiter
from sqlalchemy.exc import IntegrityError

from models.Usuarios import Usuario
from schema.usuario_schema import UsuarioSchema
from schema.completarCadastro_schema import CompletarCadastroSchema
from helpers.database import db

usuarios_bp = Blueprint("usuarios", __name__)

usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)
completar_schema = CompletarCadastroSchema()

logger = logging.getLogger(__name__)


@usuarios_bp.route("/usuarios/me", methods=["GET"])
@jwt_required()
def get_usuario_logado():
    user_id = get_jwt_identity()

    usuario = Usuario.query.get(user_id)

    return jsonify({
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "photo": usuario.photo,
        "comercio": usuario.comercio.nome_comercio if usuario.comercio else None
    })


@usuarios_bp.route("/usuarios", methods=["POST"])
@jwt_required()
def criar_usuario():
    try:
        dados = usuario_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # 🔥 VERIFICA ANTES (melhor UX)
    usuario_existente = Usuario.query.filter_by(email=dados["email"]).first()
    if usuario_existente:
        logger.warning(f"TENTATIVA EMAIL DUPLICADO | EMAIL: {dados['email']}")
        return jsonify({"error": "Email já cadastrado"}), 409

    usuario = Usuario(
        nome=dados["nome"],
        email=dados["email"],
        cpf=dados.get("cpf"),
        senha=generate_password_hash(dados["senha"]),
        cadastro_completo=True
    )

    try:
        db.session.add(usuario)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        logger.error(f"ERRO BANCO (EMAIL DUPLICADO) | EMAIL: {dados['email']}")
        return jsonify({"error": "Email já cadastrado"}), 409

    return usuario_schema.dump(usuario), 201

@usuarios_bp.route("/usuarios/login", methods=["POST"])
@limiter.limit("5 per minute")
@limiter.limit("20 per hour")
def login():
    data = request.get_json(silent=True) or {}
    ip = request.remote_addr

    if not data:
        logger.warning(f"LOGIN inválido | IP: {ip}")
        return jsonify({"error": "JSON inválido"}), 400

    email = data.get("email")
    senha = data.get("senha")

    if not email or not senha:
        logger.warning(f"LOGIN incompleto | IP: {ip} | EMAIL: {email}")
        return jsonify({"error": "Credenciais inválidas"}), 401

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not usuario.senha or not check_password_hash(usuario.senha, senha):
        logger.warning(f"LOGIN falhou | IP: {ip} | EMAIL: {email}")
        return jsonify({"error": "Credenciais inválidas"}), 401

    logger.info(f"LOGIN sucesso | IP: {ip} | USER_ID: {usuario.id}")

    access_token = create_access_token(identity=str(usuario.id))

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email
        }
    }), 200

@usuarios_bp.route("/usuarios/completar-cadastro", methods=["POST"])
@jwt_required()
def completar_cadastro():

    json_data = request.get_json()
    print("JSON RECEBIDO:", json_data)

    try:
        data = completar_schema.load(json_data)
    except ValidationError as err:
        print("ERRO DE VALIDAÇÃO:", err.messages)
        return jsonify(err.messages), 422
    
    user_id = int(get_jwt_identity())

    usuario = Usuario.query.get(user_id)

    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    usuario.cpf = data["cpf"]
    usuario.senha = generate_password_hash(data["senha"])
    usuario.cadastro_completo = True

    db.session.commit()

    return jsonify({"msg": "Cadastro completo"}), 200

@usuarios_bp.route("/usuarios/<int:id>", methods=["PUT"])
@jwt_required()
def atualizar_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    try:
        dados = usuario_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    if "nome" in dados:
        usuario.nome = dados["nome"]

    if "email" in dados:
        usuario.email = dados["email"]

    if "cpf" in dados:
        usuario.cpf = dados["cpf"]

    if "senha" in dados:
        usuario.senha = generate_password_hash(dados["senha"])

    db.session.commit()
    return usuario_schema.dump(usuario), 200



@usuarios_bp.route("/usuarios/<int:id>", methods=["DELETE"])
@jwt_required()
def deletar_usuario(id):
    usuario = Usuario.query.get(id)

    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({"message": "Usuário deletado com sucesso"}), 200
