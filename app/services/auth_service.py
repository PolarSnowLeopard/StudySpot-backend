from flask_jwt_extended import create_access_token
from ..models.user import User
from ..models.db import db

class AuthService:
    @staticmethod
    def login(username, password, role):
        """用户登录服务

        Args:
            username (str): 用户名/学号
            password (str): 密码
            role (str): 角色类型 student/admin

        Returns:
            dict: 包含token和用户信息的字典，如果登录失败则返回None
        """
        # 查找用户
        user = User.query.filter_by(username=username, role=role).first()
        
        # 验证用户存在且密码正确
        if user and user.check_password(password):
            # 创建JWT令牌
            access_token = create_access_token(identity=user.id)
            
            # 返回用户信息和令牌
            return {
                'token': access_token,
                'userId': str(user.id),
                'role': user.role,
                'name': user.name,
                'avatar': user.avatar or ''
            }
        
        return None
    
    @staticmethod
    def logout():
        """用户登出服务
        注意：由于使用JWT，实际的登出动作应该在客户端完成（删除token）
        这里服务端可以进行一些额外的清理工作
        
        Returns:
            bool: 登出是否成功
        """
        # JWT是无状态的，服务端不需要做特殊处理
        # 如果需要实现服务端登出，可以使用token黑名单等方式
        
        return True 