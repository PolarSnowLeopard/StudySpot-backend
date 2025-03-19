from marshmallow import Schema, fields, validate

class LoginSchema(Schema):
    """登录请求数据验证Schema"""
    username = fields.String(required=True, error_messages={"required": "用户名不能为空"})
    password = fields.String(required=True, error_messages={"required": "密码不能为空"})
    role = fields.String(required=True, validate=validate.OneOf(["student", "admin"]), 
                        error_messages={"required": "角色不能为空", "validator_failed": "角色必须是student或admin"})

class RegisterSchema(Schema):
    """注册请求数据验证Schema"""
    username = fields.String(required=True, error_messages={"required": "用户名不能为空"})
    password = fields.String(required=True, error_messages={"required": "密码不能为空"})
    role = fields.String(required=True, validate=validate.OneOf(["student", "admin"]), 
                        error_messages={"required": "角色不能为空", "validator_failed": "角色必须是student或admin"})
    name = fields.String(required=True, error_messages={"required": "姓名不能为空"})
    avatar = fields.String(required=False) 