from datetime import datetime
from .db import db

class Reservation(db.Model):
    """预约记录模型"""
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('study_rooms.id'), nullable=False)
    
    # 预约时间
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    
    # 状态: 
    # scheduled - 已预约
    # checked_in - 已签到
    # completed - 已完成
    # cancelled - 用户取消
    # violation_no_show - 违约未签到
    status = db.Column(db.String(50), default='scheduled', nullable=False)
    
    # 关联签到记录
    check_in_id = db.Column(db.Integer, db.ForeignKey('check_ins.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 反向关系
    student = db.relationship('User', backref='reservations')
    
    room = db.relationship('StudyRoom', backref='reservations', foreign_keys=[room_id])

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'room_id': self.room_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'status': self.status,
            'check_in_id': self.check_in_id,
            'created_at': self.created_at.isoformat()
        }