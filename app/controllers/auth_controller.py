from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from ..services import AuthService
from ..schemas import LoginSchema, RegisterSchema
from ..utils import success_response, error_response

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """登录接口
    
    请求体:
    {
        "username": "string",
        "password": "string",
        "role": "string" (student或admin)
    }
    
    返回:
    {
        "code": 200,
        "message": "success",
        "data": {
            "token": "string",
            "userId": "string",
            "role": "string",
            "name": "string",
            "avatar": "string"
        }
    }
    """
    # 获取请求数据
    data = request.get_json()
    
    # 验证请求数据
    try:
        login_data = LoginSchema().load(data)
    except ValidationError as err:
        # 验证失败，返回错误信息
        return jsonify(error_response(message=str(err.messages), code=400)), 400
    
    # 调用登录服务
    result = AuthService.login(
        username=login_data['username'],
        password=login_data['password'],
        role=login_data['role']
    )
    
    # 检查登录结果
    if result:
        return jsonify(success_response(data=result, message="登录成功"))
    else:
        return jsonify(error_response(message="用户名或密码错误", code=401)), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    """注册接口
    
    请求体:
    {
        "username": "string",
        "password": "string",
        "role": "string" (student或admin),
        "name": "string",
        "avatar": "string" (可选)
    }
    
    返回:
    {
        "code": 200,
        "message": "注册成功",
        "data": {
            "token": "string",
            "userId": "string",
            "role": "string",
            "name": "string",
            "avatar": "string"
        }
    }
    """
    # 获取请求数据
    data = request.get_json()
    
    # 验证请求数据
    try:
        register_data = RegisterSchema().load(data)
    except ValidationError as err:
        # 验证失败，返回错误信息
        return jsonify(error_response(message=str(err.messages), code=400)), 400
    
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
        return jsonify(success_response(data=result, message="注册成功"))
    else:
        return jsonify(error_response(message=error_msg, code=400)), 400

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """登出接口
    
    返回:
    {
        "code": 200,
        "message": "success"
    }
    """
    # 调用登出服务
    AuthService.logout()
    
    # 返回成功响应
    return jsonify(success_response(message="登出成功")) 