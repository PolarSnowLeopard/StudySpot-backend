import os
import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask
from flask_jwt_extended import JWTManager
from .models.db import db
from flask_cors import CORS
from flask_migrate import Migrate
from config import config_by_name
from apscheduler.schedulers.background import BackgroundScheduler

def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate = Migrate(app, db)
    JWTManager(app)
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # 注册唯一的 API 蓝图
    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # 只有在非测试环境下才启动定时任务
    if config_name != 'test' and not app.config.get('TESTING'):
        scheduler = BackgroundScheduler()
        from .tasks import setup_qrcode_tasks, setup_violation_tasks
        setup_qrcode_tasks(app, scheduler)
        setup_violation_tasks(app, scheduler)
        
        if not scheduler.running:
            try:
                scheduler.start()
                # 确保应用终止时停止调度器
                import atexit
                atexit.register(lambda: scheduler.shutdown())
            except (KeyboardInterrupt, SystemExit):
                scheduler.shutdown()

    # 打印所有已注册的路由，用于调试
    print("已注册的路由:")
    for rule in app.url_map.iter_rules():
        print(f"Endpoint: {rule.endpoint}, Path: {rule.rule}, Methods: {','.join(rule.methods)}")
        
    return app