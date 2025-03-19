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
    def register(username, password, role, name, avatar=None):
        """用户注册服务

        Args:
            username (str): 用户名/学号
            password (str): 密码
            role (str): 角色类型 student/admin
            name (str): 用户姓名
            avatar (str, optional): 头像URL. Defaults to None.

        Returns:
            dict: 包含token和用户信息的字典，如果注册失败则返回False
            str: 错误信息（如果失败）
        """
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return False, "用户名已存在"
        
        try:
            # 创建新用户
            new_user = User(
                username=username,
                password=password,
                role=role,
                name=name,
                avatar=avatar
            )
            
            # 保存到数据库
            db.session.add(new_user)
            db.session.commit()
            
            # 创建JWT令牌
            access_token = create_access_token(identity=new_user.id)
            
            # 返回用户信息和令牌
            return {
                'token': access_token,
                'userId': str(new_user.id),
                'role': new_user.role,
                'name': new_user.name,
                'avatar': new_user.avatar or ''
            }, None
        except Exception as e:
            db.session.rollback()
            return False, f"注册失败: {str(e)}"
    
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