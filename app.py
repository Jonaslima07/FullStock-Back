from flask import Flask
from dotenv import load_dotenv
import os
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from helpers import cors
from extensions.cache import cache
from helpers.database import db
from resources.Usuarios import usuarios_bp
from resources.Produtos import produtos_bp
from resources.Comercios import comercios_bp
from resources.AuthFirebase import authFirebase_bp
from flask_jwt_extended import JWTManager
from helpers.firebase import firebase_conf

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")

REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL:
    app.config.update({
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_URL": REDIS_URL,
        "CACHE_DEFAULT_TIMEOUT": 60
    })

cors.init_app(app)

db.init_app(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
cache.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(usuarios_bp)
app.register_blueprint(produtos_bp)
app.register_blueprint(comercios_bp)
app.register_blueprint(authFirebase_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
