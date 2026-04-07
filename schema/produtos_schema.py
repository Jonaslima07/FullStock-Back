from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class ProdutoSchema(Schema):
    id = fields.Int(dump_only=True)

    nome = fields.Str(
        required=True,
        validate=validate.Length(min=3)
    )

    categoria = fields.Str(
        required=True,
        validate=validate.Length(min=3)
    )

    tipo = fields.Str(
        required=True,
        validate=validate.Length(min=5)
    )

    quantidade = fields.Int(
        required=True,
        validate=validate.Range(min=0)
    )

    unidade = fields.Str(
        required=True,
        validate=validate.Length(min=2)
    )

    preco = fields.Float(
        required=True,
        validate=validate.Range(min=0)
    )

    marca = fields.Str(
        required=True,
        validate=validate.Length(min=2)
    )

    data_validade = fields.Date(
        required=True,
        format="%Y-%m-%d"
    )
