from datetime import datetime
from .db import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' 或 'admin'
    name = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    
    # 新增字段
    violation_count = db.Column(db.Integer, default=0)
    banned_until = db.Column(db.DateTime, nullable=True) # 禁用预约的截止时间
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, username, password, role, name, avatar=None):
        self.username = username
        self.set_password(password)
        self.role = role
        self.name = name
        self.avatar = avatar

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'name': self.name,
            'avatar': self.avatar,
            'violation_count': self.violation_count,
            'banned_until': self.banned_until.isoformat() if self.banned_until else None
        }