from flask import Flask
from flask_cors import CORS
from api.endpoints import kunjungan_bp


api = Flask(__name__)
CORS(api)

api.register_blueprint(kunjungan_bp)
