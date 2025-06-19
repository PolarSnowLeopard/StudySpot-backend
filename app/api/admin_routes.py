from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from ..models.db import db # <--- 确保这行是正确的！
from ..models import SystemSetting, Reservation, User, StudyRoom
from ..utils import success_response, error_response
from ..schemas import SettingUpdateSchema
from marshmallow import ValidationError
from . import api_bp

def admin_required(fn):
    """装饰器：检查用户是否为管理员"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        if user and user.role == 'admin':
            return fn(*args, **kwargs)
        else:
            return jsonify(error_response("需要管理员权限", 403)), 403
    return wrapper

@api_bp.route('/admin/settings', methods=['GET', 'POST'], endpoint='admin_manage_settings')
@admin_required
def manage_settings():
    """获取或更新系统配置"""
    if request.method == 'GET':
        settings = SystemSetting.query.all()
        data = [s.to_dict() for s in settings]
        return jsonify(success_response(data=data))
    
    if request.method == 'POST':
        data = request.json
        try:
            if isinstance(data, list):
                for item in data:
                    validated_data = SettingUpdateSchema().load(item)
                    setting = db.session.get(SystemSetting, validated_data['key'])
                    if setting:
                        setting.value = validated_data['value']
            else:
                 validated_data = SettingUpdateSchema().load(data)
                 setting = db.session.get(SystemSetting, validated_data['key'])
                 if setting:
                     setting.value = validated_data['value']
                 else:
                     return jsonify(error_response(f"配置项 {validated_data['key']} 不存在", 404)), 404
        except ValidationError as err:
            return jsonify(error_response(str(err.messages), 400)), 400
        
        db.session.commit()
        return jsonify(success_response(message="配置更新成功"))

@api_bp.route('/admin/violations/all', methods=['GET'], endpoint='admin_get_all_violations')
@admin_required
def get_all_violations():
    """获取系统中的所有违约记录"""
    violations_query = db.session.query(
        Reservation, User.name.label('student_name'), StudyRoom.name.label('room_name')
    ).join(User, Reservation.student_id == User.id)\
     .join(StudyRoom, Reservation.room_id == StudyRoom.id)\
     .filter(Reservation.status.like('violation%'))\
     .order_by(Reservation.start_time.desc()).all()
    
    results = []
    for res, student_name, room_name in violations_query:
        record = res.to_dict()
        record['student_name'] = student_name
        record['room_name'] = room_name
        results.append(record)
        
    return jsonify(success_response(data=results))

@api_bp.route('/admin/violations/stats/high-frequency-users', methods=['GET'], endpoint='admin_get_high_frequency_violators')
@admin_required
def get_high_frequency_violators():
    """获取高频违约学生名单"""
    users = User.query.filter(User.violation_count > 0).order_by(User.violation_count.desc()).limit(20).all()
    data = [u.to_dict() for u in users]
    return jsonify(success_response(data=data))