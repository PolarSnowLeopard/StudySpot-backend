from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services import QRCodeService
from ..models import User, StudyRoom
from ..utils import success_response, error_response

# 创建命名空间
api = Namespace('qrcode', description='自习室二维码相关操作')

# 定义响应模型
qrcode_display_model = api.model('QRCodeDisplay', {
    'room_id': fields.Integer(description='自习室ID'),
    'room_name': fields.String(description='自习室名称'),
    'room_location': fields.String(description='自习室位置'),
    'qrcode_data': fields.String(description='二维码数据，用于显示'),
    'expires_in': fields.Integer(description='过期时间（秒）')
})

# 定义路由
@api.route('/room/<int:room_id>')
class RoomQRCodeResource(Resource):
    @api.doc('获取自习室二维码')
    @api.response(200, '获取成功', qrcode_display_model)
    @api.response(404, '自习室不存在')
    @jwt_required()
    def get(self, room_id):
        """获取自习室的当前二维码，用于显示在大屏幕上"""
        # 验证用户权限（此处可以根据需求限制只有管理员可以获取）
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return error_response(message="只有管理员可以获取二维码", code=403), 403
        
        # 检查自习室是否存在
        room = StudyRoom.query.get(room_id)
        if not room:
            return error_response(message="自习室不存在", code=404), 404
        
        # 获取或生成二维码
        qrcode_data = QRCodeService.get_active_qrcode(room_id)
        
        # 编码二维码数据用于前端显示
        encoded_data = QRCodeService.encode_qrcode_for_display(qrcode_data)
        
        # 计算过期时间（秒）
        expires_at = qrcode_data['data']['expires_at']
        from datetime import datetime
        expires_in = max(0, (datetime.fromisoformat(expires_at) - datetime.utcnow()).total_seconds())
        
        # 返回结果
        return success_response(data={
            'room_id': room_id,
            'room_name': room.name,
            'room_location': room.location,
            'qrcode_data': encoded_data,
            'expires_in': int(expires_in)
        })
    
    @api.doc('刷新自习室二维码')
    @api.response(200, '刷新成功', qrcode_display_model)
    @api.response(404, '自习室不存在')
    @jwt_required()
    def post(self, room_id):
        """手动刷新自习室二维码"""
        # 验证用户权限
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return error_response(message="只有管理员可以刷新二维码", code=403), 403
        
        # 检查自习室是否存在
        room = StudyRoom.query.get(room_id)
        if not room:
            return error_response(message="自习室不存在", code=404), 404
        
        # 生成新的二维码
        qrcode_data = QRCodeService.generate_room_qrcode(room_id)
        
        # 编码二维码数据用于前端显示
        encoded_data = QRCodeService.encode_qrcode_for_display(qrcode_data)
        
        # 计算过期时间（秒）
        expires_at = qrcode_data['data']['expires_at']
        from datetime import datetime
        expires_in = max(0, (datetime.fromisoformat(expires_at) - datetime.utcnow()).total_seconds())
        
        # 返回结果
        return success_response(data={
            'room_id': room_id,
            'room_name': room.name,
            'room_location': room.location,
            'qrcode_data': encoded_data,
            'expires_in': int(expires_in)
        }) 