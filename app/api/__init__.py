from flask_restx import Api
from flask import Blueprint

api_bp = Blueprint('api', __name__)

api = Api(
    api_bp,
    version='1.0',
    title='自习室预约系统API',
    description='自习室预约系统的RESTful API文档',
    doc='/docs',
)

from .auth_namespace import api as auth_ns
from .qrcode_namespace import api as qrcode_ns
from .check_in_namespace import api as check_in_ns

from . import reservation_routes
from . import admin_routes
from .reserve_namespace import api as reserve_namespace
from .search_namespace import api as search_namespace

# 添加命名空间
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(qrcode_ns, path='/qrcode')
api.add_namespace(check_in_ns, path='/checkin')
api.add_namespace(reserve_namespace, path='/reserve')
api.add_namespace(search_namespace, path='/search')
