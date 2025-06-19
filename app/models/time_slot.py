from .db import db
from datetime import time, datetime

class TimeSlot(db.Model):
    __tablename__ = 'time_slots'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, nullable=False)  # 可与 Room 表关联
    seat_id = db.Column(db.Integer, nullable=False)  # 可与 Seat 表关联

    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    is_reserved = db.Column(db.Boolean, default=False)
    reserved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 用户ID

    def __repr__(self):
        return f'<Slot {self.start_time}-{self.end_time}, Seat {self.seat_id}, Reserved={self.is_reserved}>'
