from datetime import datetime
import uuid
from .db import db

class QRCode(db.Model):
    """自习室签到二维码模型"""
    __tablename__ = 'qrcodes'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('study_rooms.id'), nullable=False)
    
    # 用于验证的唯一码
    code = db.Column(db.String(32), nullable=False, unique=True)
    
    # 二维码状态
    is_active = db.Column(db.Boolean, default=True)
    
    # 时间记录
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # 反向关系
    check_ins = db.relationship('CheckIn', backref='qrcode', lazy='dynamic')
    
    @classmethod
    def generate_code(cls):
        """生成唯一的验证码"""
        return str(uuid.uuid4()).replace('-', '')
    
    def is_expired(self):
        """检查二维码是否已过期"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'code': self.code,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        } 