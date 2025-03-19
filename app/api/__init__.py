from flask_restx import Api
from flask import Blueprint

api_bp = Blueprint('api', __name__)

# 创建API实例
api = Api(
    app=api_bp,
    version='1.0',
    title='自习室预约系统API',
    description='自习室预约系统的RESTful API文档',
    doc='/docs',
)

# 导入命名空间
from .auth_namespace import api as auth_ns

# 添加命名空间
api.add_namespace(auth_ns, path='/auth') 