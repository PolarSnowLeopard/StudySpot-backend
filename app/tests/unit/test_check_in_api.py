import pytest
import json
from flask import Flask
from flask_restx import Api
from app import create_app
from app.models import User, StudyRoom, QRCode
from app.models.db import db
from app.api.check_in_namespace import api as check_in_ns
from app.services.qrcode_service import QRCodeService
from flask_jwt_extended import create_access_token

class TestCheckInAPI:
    @pytest.fixture
    def app(self):
        app = create_app('test')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        
        with app.app_context():
            db.create_all()
            
            # 创建测试学生
            student = User(
                username='test_student',
                password='password',
                role='student',
                name='测试学生'
            )
            
            # 创建测试自习室
            room = StudyRoom(
                name='测试自习室',
                location='测试位置',
                qrcode_refresh_interval=30
            )
            
            db.session.add(student)
            db.session.add(room)
            db.session.commit()
            
            # 生成有效的二维码
            from datetime import datetime, timedelta
            expires_at = datetime.utcnow() + timedelta(minutes=30)
            qrcode = QRCode(
                room_id=room.id,
                code=QRCode.generate_code(),
                expires_at=expires_at,
                is_active=True
            )
            
            db.session.add(qrcode)
            db.session.commit()
            
        yield app
        
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def student_token(self, app):
        """创建学生的JWT令牌"""
        with app.app_context():
            student = User.query.filter_by(username='test_student').first()
            # 修正点: 将 student.id 转为字符串
            token = create_access_token(identity=str(student.id))
            return token
    
    def test_student_receives_confirmation_message_on_check_in(self, app, student_token):
        """学生应该在签到成功后收到确认消息"""
        with app.app_context():
            # 获取测试数据
            student = User.query.filter_by(username='test_student').first()
            room = StudyRoom.query.filter_by(name='测试自习室').first()
            qrcode = QRCode.query.filter_by(room_id=room.id).first()
            
            # 准备二维码数据
            qrcode_data = {
                'data': {
                    'room_id': room.id,
                    'code': qrcode.code,
                    'expires_at': qrcode.expires_at.isoformat()
                }
            }
            
            # 添加签名
            qrcode_data['signature'] = QRCodeService.generate_signature(qrcode_data['data'])
            
            # 编码二维码数据
            encoded_qrcode = QRCodeService.encode_qrcode_for_display(qrcode_data)
            
            # 创建测试客户端
            client = app.test_client()
            
            # 发送签到请求
            response = client.post(
                '/api/checkin/scan',
                data=json.dumps({'qrcode': encoded_qrcode}),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {student_token}'
                }
            )
            
            # 验证响应
            data = json.loads(response.data)
            assert response.status_code == 200
            assert data['code'] == 200
            assert data['message'] == '签到成功'
            assert 'data' in data
            assert 'check_in_id' in data['data']
            assert 'room_name' in data['data']
            assert 'check_in_time' in data['data']
    
    def test_student_receives_error_message_on_failed_check_in(self, app, student_token):
        """学生应该在签到失败时收到错误消息"""
        with app.app_context():
            # 创建测试客户端
            client = app.test_client()
            
            # 发送无效的签到请求
            response = client.post(
                '/api/checkin/scan',
                data=json.dumps({'qrcode': 'invalid_qrcode_data'}),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {student_token}'
                }
            )
            
            # 验证响应
            data = json.loads(response.data)
            assert response.status_code == 400
            assert data['code'] == 400
            assert '无效的二维码格式' in data['message']