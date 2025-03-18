from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ..services import AuthService
from ..utils import success_response, error_response

# 创建命名空间
api = Namespace('auth', description='认证相关操作')

# 定义请求模型
login_request = api.model('LoginRequest', {
    'username': fields.String(required=True, description='用户名/学号'),
    'password': fields.String(required=True, description='密码'),
    'role': fields.String(required=True, description='角色：student或admin', enum=['student', 'admin'])
})

# 定义响应模型
user_info = api.model('UserInfo', {
    'userId': fields.String(description='用户ID'),
    'role': fields.String(description='角色'),
    'name': fields.String(description='姓名'),
    'avatar': fields.String(description='头像URL')
})

login_response = api.model('LoginResponse', {
    'code': fields.Integer(description='状态码：0表示成功，非0表示失败'),
    'message': fields.String(description='响应消息'),
    'data': fields.Nested(api.model('LoginData', {
        'token': fields.String(description='登录令牌'),
        'userId': fields.String(description='用户ID'),
        'role': fields.String(description='角色'),
        'name': fields.String(description='姓名'),
        'avatar': fields.String(description='头像URL')
    }))
})

general_response = api.model('GeneralResponse', {
    'code': fields.Integer(description='状态码：0表示成功，非0表示失败'),
    'message': fields.String(description='响应消息')
})

# 定义认证路由
@api.route('/login')
class Login(Resource):
    @api.doc('用户登录')
    @api.expect(login_request)
    @api.response(200, '登录成功', login_response)
    @api.response(401, '登录失败', general_response)
    def post(self):
        """用户登录"""
        data = request.json
        
        # 调用登录服务
        result = AuthService.login(
            username=data.get('username'),
            password=data.get('password'),
            role=data.get('role')
        )
        
        # 检查登录结果
        if result:
            return success_response(data=result, message="登录成功")
        else:
            return error_response(message="用户名或密码错误", code=401), 401


@api.route('/logout')
class Logout(Resource):
    @api.doc('用户登出')
    @api.response(200, '登出成功', general_response)
    def post(self):
        """用户登出"""
        # 调用登出服务
        AuthService.logout()
        
        # 返回成功响应
        return success_response(message="登出成功") 