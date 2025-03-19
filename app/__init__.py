import os
import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, Blueprint
from flask_jwt_extended import JWTManager
from .models.db import db
from config import config_by_name

jwt = JWTManager()

def create_app(config_name='dev'):
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config_by_name[config_name])
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    
    # 初始化Restx API
    from .api import api
    api_blueprint = Blueprint('api', __name__)
    api.init_app(api_blueprint)
    app.register_blueprint(api_blueprint)
    
    return app 