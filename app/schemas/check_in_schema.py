from marshmallow import Schema, fields, validates, ValidationError

class CheckInSchema(Schema):
    """签到请求验证模式"""
    qrcode = fields.String(required=True, error_messages={'required': '二维码数据不能为空'})

    @validates('qrcode')
    def validate_qrcode(self, value):
        if not value.strip():
            raise ValidationError('二维码数据不能为空')

class CheckOutSchema(Schema):
    """签退请求验证模式"""
    room_id = fields.Integer(required=True, error_messages={'required': '自习室ID不能为空'})

    @validates('room_id')
    def validate_room_id(self, value):
        if value <= 0:
            raise ValidationError('无效的自习室ID')

class CheckInListSchema(Schema):
    """签到记录列表请求验证模式"""
    status = fields.String(required=False)
    limit = fields.Integer(required=False, missing=10)
    offset = fields.Integer(required=False, missing=0)

    @validates('limit')
    def validate_limit(self, value):
        if value < 1 or value > 100:
            raise ValidationError('每页记录数必须在1到100之间')

    @validates('offset')
    def validate_offset(self, value):
        if value < 0:
            raise ValidationError('偏移值不能为负数') 