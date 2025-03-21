import pytest
from contextlib import contextmanager
from app import create_app
from app.services.auth_service import AuthService
from app.models.user import User
from app.models.db import db

class TestAuthService:
    @pytest.fixture
    def app(self):
        """创建测试用的Flask应用"""
        app = create_app('test')
        # 确保使用测试配置
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        # 确保在测试上下文中创建数据库表
        with app.app_context():
            db.create_all()
            
        yield app
        
        # 测试结束后清理
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    # 自定义上下文管理器，确保在应用上下文中进行模拟和清理
    @contextmanager
    def patched_context(self, app, mocker, target, **kwargs):
        with app.app_context():
            # 应用补丁
            patcher = mocker.patch(target, **kwargs)
            yield patcher
    
    def test_login_success(self, app, mocker):
        """测试登录成功的情况"""
        # 创建模拟对象
        mock_user = mocker.Mock()
        mock_user.id = 1
        mock_user.role = 'student'
        mock_user.name = '张三'
        mock_user.avatar = 'avatar_url'
        mock_user.check_password.return_value = True
        
        # 设置模拟查询
        mock_filter_by = mocker.Mock()
        mock_filter_by.first.return_value = mock_user
        
        mock_query = mocker.Mock()
        mock_query.filter_by.return_value = mock_filter_by
        
        # 在应用上下文中应用补丁
        with app.app_context():
            # 应用补丁
            mocker.patch('app.services.auth_service.User.query', mock_query)
            mocker.patch('app.services.auth_service.create_access_token', return_value='fake_token')
            
            # 执行登录
            result = AuthService.login('test_user', 'password', 'student')
            
            # 验证结果
            assert result is not None
            assert result['token'] == 'fake_token'
            assert result['userId'] == '1'
            assert result['role'] == 'student'
            assert result['name'] == '张三'
            assert result['avatar'] == 'avatar_url'
            
            # 确保补丁在应用上下文中被停止
            mocker.stopall()
        
    def test_login_failure_wrong_password(self, app, mocker):
        """测试登录失败-密码错误的情况"""
        # 在应用上下文中进行测试
        with app.app_context():
            # 模拟用户查询
            mock_user = mocker.Mock()
            mock_user.check_password.return_value = False
            
            # 设置模拟查询
            mock_filter_by = mocker.Mock()
            mock_filter_by.first.return_value = mock_user
            
            mock_query = mocker.Mock()
            mock_query.filter_by.return_value = mock_filter_by
            
            # 应用补丁
            mocker.patch('app.services.auth_service.User.query', mock_query)
            
            # 执行登录
            result = AuthService.login('test_user', 'wrong_password', 'student')
            
            # 验证结果
            assert result is None
            
            # 确保补丁在应用上下文中被停止
            mocker.stopall()
        
    def test_login_failure_user_not_found(self, app, mocker):
        """测试登录失败-用户不存在的情况"""
        # 在应用上下文中进行测试
        with app.app_context():
            # 设置模拟查询
            mock_filter_by = mocker.Mock()
            mock_filter_by.first.return_value = None
            
            mock_query = mocker.Mock()
            mock_query.filter_by.return_value = mock_filter_by
            
            # 应用补丁
            mocker.patch('app.services.auth_service.User.query', mock_query)
            
            # 执行登录
            result = AuthService.login('non_existent_user', 'password', 'student')
            
            # 验证结果
            assert result is None
            
            # 确保补丁在应用上下文中被停止
            mocker.stopall()
        
    def test_logout(self):
        """测试登出功能"""
        # 登出服务应该始终返回True
        assert AuthService.logout() is True 