from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from api.endpoints import kunjungan_bp


api = Flask(__name__)
CORS(api)

api.config['JWT_SECRET_KEY'] = 'c06c5bbd202332b1ac34e7c0bd3ec660'
jwt = JWTManager(api)

api.register_blueprint(kunjungan_bp)
