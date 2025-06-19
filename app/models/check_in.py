from datetime import datetime
from .db import db

class CheckIn(db.Model):
    """学生签到记录模型"""
    __tablename__ = 'check_ins'

    id = db.Column(db.Integer, primary_key=True)
    
    # 关联信息
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('study_rooms.id'), nullable=False)
    qrcode_id = db.Column(db.Integer, db.ForeignKey('qrcodes.id'), nullable=False)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.id'), nullable=True) # 新增字段

    # 签到状态：checked_in(已签到), checked_out(已签退), expired(过期)
    status = db.Column(db.String(20), default='checked_in')
    
    # 时间记录
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow)
    check_out_time = db.Column(db.DateTime)
    
    # 学习时长（分钟）
    duration = db.Column(db.Integer)
    
    # 违约标记（是否未签到而被自动取消）
    is_violation = db.Column(db.Boolean, default=False)
    
    # 反向关系
    student = db.relationship('User', backref='check_ins')
    
    # 修正点: 使用 foreign_keys 参数明确指定外键
    reservation = db.relationship(
        'Reservation', 
        backref='check_in_record', 
        uselist=False, 
        foreign_keys=[reservation_id] 
    )
    
    def calculate_duration(self):
        """计算学习时长（分钟）"""
        if self.check_out_time and self.check_in_time:
            delta = self.check_out_time - self.check_in_time
            return int(delta.total_seconds() / 60)
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'room_id': self.room_id,
            'qrcode_id': self.qrcode_id,
            'reservation_id': self.reservation_id, # 新增
            'status': self.status,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'duration': self.duration,
            'is_violation': self.is_violation
        }