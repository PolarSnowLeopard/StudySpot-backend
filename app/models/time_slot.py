from .db import db
from datetime import time, datetime

class TimeSlot(db.Model):
    __tablename__ = 'time_slots'

    id = db.Column(db.Integer, primary_key=True)
    # room_id = db.Column(db.Integer, nullable=False)
    # seat_id = db.Column(db.Integer, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('study_rooms.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seat.id'), nullable=False)

    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    is_reserved = db.Column(db.Boolean, default=False)
    reserved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 用户ID

    room = db.relationship('StudyRoom', backref='time_slots')
    seat = db.relationship('Seat', backref='time_slots')
    user = db.relationship('User', backref='time_slots')

    def __repr__(self):
        return f'<Slot {self.start_time}-{self.end_time}, Seat {self.seat_id}, Reserved={self.is_reserved}>'
