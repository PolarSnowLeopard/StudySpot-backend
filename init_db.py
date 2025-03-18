"""
数据库初始化脚本
用于创建数据库表结构并添加初始数据
"""
from app import create_app
from app.models.db import db
from app.models.user import User

def init_db():
    """初始化数据库"""
    app = create_app('dev')
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否已存在管理员账户
        admin = User.query.filter_by(username='admin', role='admin').first()
        if not admin:
            # 创建默认管理员账户
            admin = User(
                username='admin',
                password='admin123',  # 请在生产环境中修改此密码
                role='admin',
                name='系统管理员',
                avatar=None
            )
            db.session.add(admin)
        
        # 添加示例学生账户
        student = User.query.filter_by(username='student1', role='student').first()
        if not student:
            student = User(
                username='student1',
                password='password123',  # 请在生产环境中修改此密码
                role='student',
                name='学生测试账号',
                avatar=None
            )
            db.session.add(student)
        
        # 提交所有更改
        db.session.commit()
        
        print("数据库初始化完成！")
        print("默认管理员账号: admin / admin123")
        print("默认学生账号: student1 / password123")
        print("请在生产环境中修改这些默认密码！")

if __name__ == '__main__':
    init_db() 