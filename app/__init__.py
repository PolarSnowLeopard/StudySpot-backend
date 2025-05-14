import os
import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, Blueprint
from flask_jwt_extended import JWTManager
from .models.db import db
from flask_cors import CORS
from config import config_by_name

jwt = JWTManager()

def create_app(config_name='dev'):
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config_by_name[config_name])
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)

    # 注册CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # 初始化Restx API
    from .api import api_bp
    # api_blueprint = Blueprint('api', __name__)
    # api.init_app(api_blueprint)
    # app.register_blueprint(api_blueprint)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 设置定时任务
    if config_name != 'test':  # 测试环境不启动定时任务
        from .tasks import setup_qrcode_tasks
        setup_qrcode_tasks(app)
    
    # 添加调试输出
    print("已注册的路由:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}")
    
    return app 