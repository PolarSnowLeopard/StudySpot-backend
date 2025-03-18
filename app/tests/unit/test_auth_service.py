import pytest
from app.services.auth_service import AuthService
from app.models.user import User
from app.models.db import db

class TestAuthService:
    def test_login_success(self, mocker):
        # 模拟用户查询
        mock_user = mocker.Mock()
        mock_user.id = 1
        mock_user.role = 'student'
        mock_user.name = '张三'
        mock_user.avatar = 'avatar_url'
        mock_user.check_password.return_value = True
        
        # 模拟数据库查询
        mocker.patch('app.models.user.User.query.filter_by', return_value=mocker.Mock(
            first=lambda: mock_user
        ))
        
        # 模拟token创建
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
        
    def test_login_failure_wrong_password(self, mocker):
        # 模拟用户查询
        mock_user = mocker.Mock()
        mock_user.check_password.return_value = False
        
        # 模拟数据库查询
        mocker.patch('app.models.user.User.query.filter_by', return_value=mocker.Mock(
            first=lambda: mock_user
        ))
        
        # 执行登录
        result = AuthService.login('test_user', 'wrong_password', 'student')
        
        # 验证结果
        assert result is None
        
    def test_login_failure_user_not_found(self, mocker):
        # 模拟数据库查询
        mocker.patch('app.models.user.User.query.filter_by', return_value=mocker.Mock(
            first=lambda: None
        ))
        
        # 执行登录
        result = AuthService.login('non_existent_user', 'password', 'student')
        
        # 验证结果
        assert result is None
        
    def test_logout(self):
        # 登出服务应该始终返回True
        assert AuthService.logout() is True 