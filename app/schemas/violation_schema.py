from marshmallow import Schema, fields, validate, validates_schema, ValidationError

class ReservationRequestSchema(Schema):
    """创建预约请求验证"""
    room_id = fields.Int(required=True)
    start_time = fields.DateTime(required=True, format='iso')
    end_time = fields.DateTime(required=True, format='iso')

    # 修正点：直接使用 @validates_schema
    @validates_schema
    def validate_times(self, data, **kwargs):
        if data.get('start_time') and data.get('end_time') and data['start_time'] >= data['end_time']:
            # 修正点：直接抛出 ValidationError
            raise ValidationError("结束时间必须晚于开始时间")

class SettingUpdateSchema(Schema):
    """更新系统配置请求验证"""
    key = fields.Str(required=True)
    value = fields.Str(required=True)

class ViolationListSchema(Schema):
    """违约记录列表查询参数验证"""
    student_id = fields.Int(required=False)
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=10, validate=validate.Range(min=1, max=100))