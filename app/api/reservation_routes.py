from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.db import db  
from ..models import Reservation, Notification, StudyRoom, User
from ..utils import success_response, error_response
from . import api_bp

@api_bp.route('/reservations/', methods=['GET'], endpoint='reservations_get_list')
@jwt_required()
def get_reservations():
    """获取当前用户的预约列表"""
    student_id = get_jwt_identity()
    reservations = Reservation.query.filter_by(student_id=student_id).order_by(Reservation.start_time.desc()).all()
    data = [r.to_dict() for r in reservations]
    return jsonify(success_response(data=data))

@api_bp.route('/reservations/violations/history', methods=['GET'], endpoint='reservations_get_violation_history')
@jwt_required()
def get_violation_history():
    """获取个人违约历史"""
    student_id = get_jwt_identity()
    violations_query = db.session.query(
        Reservation, StudyRoom.name.label('room_name')
    ).join(StudyRoom, Reservation.room_id == StudyRoom.id).filter(
        Reservation.student_id == student_id,
        Reservation.status.like('violation%')
    ).order_by(Reservation.start_time.desc()).all()
    
    results = []
    for res, room_name in violations_query:
        record = res.to_dict()
        record['room_name'] = room_name
        results.append(record)
        
    return jsonify(success_response(data=results))

@api_bp.route('/reservations/notifications', methods=['GET'], endpoint='reservations_get_notifications')
@jwt_required()
def get_notifications():
    """获取个人通知列表"""
    user_id = get_jwt_identity()
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(50).all()
    data = [n.to_dict() for n in notifications]
    return jsonify(success_response(data=data))

@api_bp.route('/reservations/notifications/<int:notification_id>/read', methods=['POST'], endpoint='reservations_read_notification')
@jwt_required()
def read_notification(notification_id):
    """将通知标记为已读"""
    user_id = get_jwt_identity()
    notification = db.session.get(Notification, notification_id)
    if not notification or int(notification.user_id) != int(user_id):
        return jsonify(error_response("通知不存在", 404)), 404
    
    notification.is_read = True
    db.session.commit()
    return jsonify(success_response(message="标记已读成功"))