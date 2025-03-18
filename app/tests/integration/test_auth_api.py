import pytest
import json
from app import create_app
from app.models.user import User
from app.models.db import db

class TestAuthAPI:
    @pytest.fixture
    def app(self):
        app = create_app('test')
        app.config['TESTING'] = True
        # 使用SQLite内存数据库
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            # 创建测试用户
            test_user = User(
                username='test_student',
                password='password123',
                role='student',
                name='测试学生'
            )
            db.session.add(test_user)
            db.session.commit()
            
        yield app
        
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    def test_login_success(self, client):
        """测试登录成功的场景"""
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': 'test_student',
                'password': 'password123',
                'role': 'student'
            }),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['code'] == 0
        assert data['message'] == '登录成功'
        assert 'token' in data['data']
        assert data['data']['userId'] is not None
        assert data['data']['role'] == 'student'
        assert data['data']['name'] == '测试学生'
    
    def test_login_failure(self, client):
        """测试登录失败的场景"""
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': 'test_student',
                'password': 'wrong_password',
                'role': 'student'
            }),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        assert response.status_code == 401
        assert data['code'] == 401
        assert data['message'] == '用户名或密码错误'
    
    def test_logout(self, client):
        """测试登出功能"""
        response = client.post('/api/auth/logout')
        
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['code'] == 0
        assert data['message'] == '登出成功' 