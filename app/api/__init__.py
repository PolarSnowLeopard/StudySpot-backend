from flask_restx import Api

# 创建API实例
api = Api(
    version='1.0',
    title='自习室预约系统API',
    description='自习室预约系统的RESTful API文档',
    doc='/api/docs',
    prefix='/api'
)

# 导入命名空间
from .auth_namespace import api as auth_ns

# 添加命名空间
api.add_namespace(auth_ns, path='/auth') 