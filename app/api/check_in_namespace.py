from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from ..services import CheckInService
from ..schemas import CheckInSchema, CheckOutSchema, CheckInListSchema
from ..models import User
from ..utils import success_response, error_response

# 创建命名空间
api = Namespace('checkin', description='学生签到相关操作')

# 定义请求模型
check_in_model = api.model('CheckInRequest', {
    'qrcode': fields.String(required=True, description='二维码数据')
})

check_out_model = api.model('CheckOutRequest', {
    'room_id': fields.Integer(required=True, description='自习室ID')
})

# 定义响应模型
check_in_response = api.model('CheckInResponse', {
    'check_in_id': fields.Integer(description='签到记录ID'),
    'room_name': fields.String(description='自习室名称'),
    'room_location': fields.String(description='自习室位置'),
    'check_in_time': fields.String(description='签到时间')
})

check_out_response = api.model('CheckOutResponse', {
    'check_in_id': fields.Integer(description='签到记录ID'),
    'duration': fields.Integer(description='学习时长（分钟）'),
    'check_out_time': fields.String(description='签退时间')
})

check_in_history_item = api.model('CheckInHistoryItem', {
    'id': fields.Integer(description='签到记录ID'),
    'room_name': fields.String(description='自习室名称'),
    'room_location': fields.String(description='自习室位置'),
    'check_in_time': fields.String(description='签到时间'),
    'check_out_time': fields.String(description='签退时间'),
    'duration': fields.Integer(description='学习时长（分钟）'),
    'status': fields.String(description='签到状态')
})

check_in_history_response = api.model('CheckInHistoryResponse', {
    'data': fields.List(fields.Nested(check_in_history_item))
})

# 定义路由
@api.route('/scan')
class CheckInResource(Resource):
    @api.doc('学生签到')
    @api.expect(check_in_model)
    @api.response(200, '签到成功', check_in_response)
    @api.response(400, '无效的请求')
    @api.response(401, '未授权')
    @jwt_required()
    def post(self):
        """学生扫码签到"""
        # 获取当前用户ID
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # 验证用户角色
        if not user or user.role != 'student':
            return error_response(message="只有学生可以使用签到功能", code=403), 403
        
        # 验证请求数据
        try:
            data = CheckInSchema().load(request.json)
        except ValidationError as err:
            return error_response(message=str(err.messages), code=400), 400
        
        # 处理签到
        result = CheckInService.student_check_in(current_user_id, data['qrcode'])
        
        # 判断处理结果
        if result['success']:
            return success_response(data=result['data'], message="签到成功")
        else:
            return error_response(message=result['message'], code=400), 400

@api.route('/checkout')
class CheckOutResource(Resource):
    @api.doc('学生签退')
    @api.expect(check_out_model)
    @api.response(200, '签退成功', check_out_response)
    @api.response(400, '无效的请求')
    @api.response(401, '未授权')
    @jwt_required()
    def post(self):
        """学生签退"""
        # 获取当前用户ID
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # 验证用户角色
        if not user or user.role != 'student':
            return error_response(message="只有学生可以使用签退功能", code=403), 403
        
        # 验证请求数据
        try:
            data = CheckOutSchema().load(request.json)
        except ValidationError as err:
            return error_response(message=str(err.messages), code=400), 400
        
        # 处理签退
        result = CheckInService.student_check_out(current_user_id, data['room_id'])
        
        # 判断处理结果
        if result['success']:
            return success_response(data=result['data'], message="签退成功")
        else:
            return error_response(message=result['message'], code=400), 400

@api.route('/history')
class CheckInHistoryResource(Resource):
    @api.doc('获取签到历史')
    @api.response(200, '获取成功', check_in_history_response)
    @api.response(401, '未授权')
    @jwt_required()
    def get(self):
        """获取学生签到历史记录"""
        # 获取当前用户ID
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # 验证用户角色
        if not user or user.role != 'student':
            return error_response(message="只有学生可以查看签到历史", code=403), 403
        
        # 获取查询参数
        try:
            params = CheckInListSchema().load({
                'status': request.args.get('status'),
                'limit': request.args.get('limit', 10, type=int),
                'offset': request.args.get('offset', 0, type=int)
            })
        except ValidationError as err:
            return error_response(message=str(err.messages), code=400), 400
        
        # 获取历史记录
        result = CheckInService.get_student_check_ins(
            current_user_id,
            status=params.get('status'),
            limit=params.get('limit'),
            offset=params.get('offset')
        )
        
        # 判断处理结果
        if result['success']:
            return success_response(data=result['data'])
        else:
            return error_response(message=result['message'], code=400), 400 