# app/tests/unit/test_check_in_service.py
import pytest
import json
from datetime import datetime, timedelta
from app import create_app
from app.models import User, StudyRoom, QRCode, CheckIn
from app.models.db import db
from app.services.qrcode_service import QRCodeService
from app.services.check_in_service import CheckInService

class TestStudentCheckIn:
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
    
    def test_student_can_check_in_with_valid_qrcode(self, app):
        """学生应该能使用有效的二维码签到"""
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
            
            # 执行签到
            result = CheckInService.student_check_in(student.id, encoded_qrcode)
            
            # 验证结果
            assert result['success'] == True
            assert '签到成功' in result['message']
            assert 'check_in_id' in result['data']
            assert result['data']['room_name'] == room.name
            
            # 验证数据库中的签到记录
            check_in = CheckIn.query.filter_by(student_id=student.id, room_id=room.id).first()
            assert check_in is not None
            assert check_in.status == 'checked_in'
    
    def test_student_cannot_check_in_with_expired_qrcode(self, app):
        """学生不能使用过期的二维码签到"""
        with app.app_context():
            # 获取测试数据
            student = User.query.filter_by(username='test_student').first()
            room = StudyRoom.query.filter_by(name='测试自习室').first()
            
            # 创建过期的二维码
            expired_qrcode = QRCode(
                room_id=room.id,
                code=QRCode.generate_code(),
                expires_at=datetime.utcnow() - timedelta(minutes=5),  # 已过期
                is_active=True
            )
            
            db.session.add(expired_qrcode)
            db.session.commit()
            
            # 准备二维码数据
            qrcode_data = {
                'data': {
                    'room_id': room.id,
                    'code': expired_qrcode.code,
                    'expires_at': expired_qrcode.expires_at.isoformat()
                }
            }
            
            # 添加签名
            qrcode_data['signature'] = QRCodeService.generate_signature(qrcode_data['data'])
            
            # 编码二维码数据
            encoded_qrcode = QRCodeService.encode_qrcode_for_display(qrcode_data)
            
            # 执行签到
            result = CheckInService.student_check_in(student.id, encoded_qrcode)
            
            # 验证结果
            assert result['success'] == False
            assert '二维码已过期' in result['message']
            
            # 验证数据库中没有签到记录
            check_in = CheckIn.query.filter_by(student_id=student.id, room_id=room.id).first()
            assert check_in is None
    
    def test_student_cannot_check_in_twice(self, app):
        """学生不能在同一自习室重复签到"""
        with app.app_context():
            # 获取测试数据
            student = User.query.filter_by(username='test_student').first()
            room = StudyRoom.query.filter_by(name='测试自习室').first()
            qrcode = QRCode.query.filter_by(room_id=room.id).first()
            
            # 创建已有的签到记录
            existing_check_in = CheckIn(
                student_id=student.id,
                room_id=room.id,
                qrcode_id=qrcode.id,
                status='checked_in'
            )
            
            db.session.add(existing_check_in)
            db.session.commit()
            
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
            
            # 执行签到
            result = CheckInService.student_check_in(student.id, encoded_qrcode)
            
            # 验证结果
            assert result['success'] == False
            assert '您已经在该自习室签到' in result['message']