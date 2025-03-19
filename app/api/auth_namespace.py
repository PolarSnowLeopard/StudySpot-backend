from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ..services import AuthService
from ..utils import success_response, error_response
from marshmallow import ValidationError
from ..schemas import LoginSchema, RegisterSchema

# 创建命名空间
api = Namespace('auth', description='认证相关操作')

# 定义请求模型
login_request = api.model('LoginRequest', {
    'username': fields.String(required=True, description='用户名/学号'),
    'password': fields.String(required=True, description='密码'),
    'role': fields.String(required=True, description='角色：student或admin', enum=['student', 'admin'])
})

register_request = api.model('RegisterRequest', {
    'username': fields.String(required=True, description='用户名/学号'),
    'password': fields.String(required=True, description='密码'),
    'role': fields.String(required=True, description='角色：student或admin', enum=['student', 'admin']),
    'name': fields.String(required=True, description='姓名'),
    'avatar': fields.String(required=False, description='头像URL')
})

# 定义统一的响应模型
auth_data = api.model('AuthData', {
    'token': fields.String(description='登录令牌'),
    'userId': fields.String(description='用户ID'),
    'role': fields.String(description='角色'),
    'name': fields.String(description='姓名'),
    'avatar': fields.String(description='头像URL')
})

base_response = api.model('BaseResponse', {
    'code': fields.Integer(description='状态码：200表示成功，其他表示失败'),
    'message': fields.String(description='响应消息'),
    'data': fields.Raw(description='响应数据')
})

auth_response = api.inherit('AuthResponse', base_response, {
    'data': fields.Nested(auth_data)
})

# 定义认证路由
@api.route('/login')
class Login(Resource):
    @api.doc('用户登录')
    @api.expect(login_request)
    @api.response(200, '登录成功', auth_response)
    @api.response(401, '登录失败', base_response)
    def post(self):
        """用户登录"""
        data = request.json
        
        # 验证请求数据
        try:
            login_data = LoginSchema().load(data)
        except ValidationError as err:
            return error_response(message=str(err.messages), code=400), 400
        
        # 调用登录服务
        result = AuthService.login(
            username=login_data['username'],
            password=login_data['password'],
            role=login_data['role']
        )
        
        # 检查登录结果
        if result:
            return success_response(data=result, message="登录成功")
        else:
            return error_response(message="用户名或密码错误", code=401), 401

@api.route('/register')
class Register(Resource):
    @api.doc('用户注册')
    @api.expect(register_request)
    @api.response(200, '注册成功', auth_response)
    @api.response(400, '注册失败', base_response)
    def post(self):
        """用户注册"""
        data = request.json
        
        # 验证请求数据
        try:
            register_data = RegisterSchema().load(data)
        except ValidationError as err:
            return error_response(message=str(err.messages), code=400), 400
        
        # 调用注册服务
        result, error_msg = AuthService.register(
            username=register_data['username'],
            password=register_data['password'],
            role=register_data['role'],
            name=register_data['name'],
            avatar=register_data.get('avatar')
        )
        
        # 检查注册结果
        if result:
            return success_response(data=result, message="注册成功")
        else:
            return error_response(message=error_msg, code=400), 400

@api.route('/logout')
class Logout(Resource):
    @api.doc('用户登出')
    @api.response(200, '登出成功', base_response)
    def post(self):
        """用户登出"""
        # 调用登出服务
        AuthService.logout()
        
        # 返回成功响应
        return success_response(message="登出成功")