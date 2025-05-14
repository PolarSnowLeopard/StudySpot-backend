from datetime import datetime
from .db import db

class StudyRoom(db.Model):
    """自习室模型"""
    __tablename__ = 'study_rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    
    # 二维码刷新间隔（分钟）
    qrcode_refresh_interval = db.Column(db.Integer, default=30)
    
    # 自习室管理员ID（可为空，表示由系统管理员管理）
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 反向关系
    qrcodes = db.relationship('QRCode', backref='room', lazy='dynamic', cascade='all, delete-orphan')
    check_ins = db.relationship('CheckIn', backref='room', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'capacity': self.capacity,
            'description': self.description,
            'qrcode_refresh_interval': self.qrcode_refresh_interval,
            'admin_id': self.admin_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 