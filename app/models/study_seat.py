from .db import db


class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    has_power = db.Column(db.Boolean, default=False)  # ✅ 是否有插头
