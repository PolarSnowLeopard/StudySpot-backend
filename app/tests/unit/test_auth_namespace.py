import pytest
import json
from flask import Flask
from flask_restx import Api
from app.api.auth_namespace import api as auth_ns
from app.services.auth_service import AuthService

class TestAuthNamespace:
    @pytest.fixture
    def app(self):
        """创建测试用的Flask应用"""
        app = Flask(__name__)
        api = Api(app)
        api.add_namespace(auth_ns, path='/api/auth')
        app.config['TESTING'] = True
        return app
    
    def test_login_success(self, app, mocker):
        # 模拟AuthService.login返回成功结果
        mock_result = {
            'token': 'fake_token',
            'userId': '1',
            'role': 'student',
            'name': '张三',
            'avatar': 'avatar_url'
        }
        mocker.patch.object(AuthService, 'login', return_value=mock_result)
        
        # 创建测试客户端
        client = app.test_client()
        
        # 发送登录请求
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': 'test_user',
                'password': 'password',
                'role': 'student'
            }),
            content_type='application/json'
        )
        
        # 验证响应
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['code'] == 200
        assert data['message'] == '登录成功'
        assert data['data']['token'] == 'fake_token'
        assert data['data']['userId'] == '1'
        assert data['data']['role'] == 'student'
        assert data['data']['name'] == '张三'
        assert data['data']['avatar'] == 'avatar_url'
        
    def test_login_failure(self, app, mocker):
        # 模拟AuthService.login返回失败结果
        mocker.patch.object(AuthService, 'login', return_value=None)
        
        # 创建测试客户端
        client = app.test_client()
        
        # 发送登录请求
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': 'test_user',
                'password': 'wrong_password',
                'role': 'student'
            }),
            content_type='application/json'
        )
        
        # 验证响应
        data = json.loads(response.data)
        assert response.status_code == 401
        assert data['code'] == 401
        assert data['message'] == '用户名或密码错误'
        
    def test_login_validation_error(self, app):
        # 创建测试客户端
        client = app.test_client()
        
        # 发送不完整的登录请求
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': 'test_user',
                # 缺少password
                'role': 'student'
            }),
            content_type='application/json'
        )
        
        # 验证响应
        data = json.loads(response.data)
        assert response.status_code == 400
        assert data['code'] == 400
        assert '密码不能为空' in data['message']
        
    def test_logout(self, app, mocker):
        # 模拟AuthService.logout
        mocker.patch.object(AuthService, 'logout', return_value=True)
        
        # 创建测试客户端
        client = app.test_client()
        
        # 发送登出请求
        response = client.post('/api/auth/logout')
        
        # 验证响应
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['code'] == 200
        assert data['message'] == '登出成功'
        
    def test_register_success(self, app, mocker):
        # 模拟AuthService.register返回成功结果
        mock_result = {
            'token': 'fake_token',
            'userId': '1',
            'role': 'student',
            'name': '张三',
            'avatar': 'avatar_url'
        }
        mocker.patch.object(AuthService, 'register', return_value=(mock_result, None))
        
        # 创建测试客户端
        client = app.test_client()
        
        # 发送注册请求
        response = client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': 'new_user',
                'password': 'password',
                'role': 'student',
                'name': '张三',
                'avatar': 'avatar_url'
            }),
            content_type='application/json'
        )
        
        # 验证响应
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['code'] == 200
        assert data['message'] == '注册成功'
        assert data['data']['token'] == 'fake_token'
        
    def test_register_failure(self, app, mocker):
        # 模拟AuthService.register返回失败结果
        mocker.patch.object(AuthService, 'register', return_value=(False, "用户名已存在"))
        
        # 创建测试客户端
        client = app.test_client()
        
        # 发送注册请求
        response = client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': 'existing_user',
                'password': 'password',
                'role': 'student',
                'name': '张三',
                'avatar': 'avatar_url'
            }),
            content_type='application/json'
        )
        
        # 验证响应
        data = json.loads(response.data)
        assert response.status_code == 400
        assert data['code'] == 400
        assert data['message'] == '用户名已存在' 