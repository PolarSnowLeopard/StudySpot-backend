import pytest
from datetime import datetime, timedelta
from app import create_app
from app.models.db import db
from app.models import User, StudyRoom, Reservation, SystemSetting, Notification
from app.services import ViolationService

@pytest.fixture(scope='module')
def app():
    """创建一个模块级别的测试应用"""
    app = create_app('test')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def session(app):
    """为每个测试函数创建一个独立的数据库会话和事务"""
    with app.app_context():
        # 清理所有表
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        
        # 修正点: 去掉所有手动指定的 id
        student1 = User(username='violator', password='pw', role='student', name='违约学生')
        student2 = User(username='good_student', password='pw', role='student', name='好学生')
        room1 = StudyRoom(name='测试自习室A', location='A')
        
        # 默认系统配置
        settings_data = [
            SystemSetting(key='REMINDER_BEFORE_MINUTES', value='15', description=''),
            SystemSetting(key='NO_SHOW_TIMEOUT_MINUTES', value='10', description=''),
            SystemSetting(key='MAX_VIOLATION_COUNT', value='3', description=''),
            SystemSetting(key='BAN_DAYS', value='7', description='')
        ]
        
        db.session.add_all([student1, student2, room1] + settings_data)
        db.session.commit()
        
        yield db.session
        
        db.session.rollback()


class TestViolationService:
    def test_check_upcoming_reservations_sends_reminder(self, session):
        """测试系统应为即将开始的预约发送提醒"""
        good_student = User.query.filter_by(username='good_student').one()
        room = StudyRoom.query.filter_by(name='测试自习室A').one()

        # 准备数据: 一个10分钟后开始的预约
        now = datetime.utcnow()
        upcoming_res = Reservation(
            student_id=good_student.id, room_id=room.id, 
            start_time=now + timedelta(minutes=10),
            end_time=now + timedelta(hours=1)
        )
        session.add(upcoming_res)
        session.commit()
        
        # 执行服务
        ViolationService.check_upcoming_reservations()
        session.commit() 

        # 验证结果
        notification = Notification.query.filter_by(user_id=good_student.id).first()
        assert notification is not None
        assert "即将于" in notification.message
        assert "开始" in notification.message

    def test_process_no_show_violations_marks_as_violation(self, session):
        """测试系统应将超时未签到的预约标记为违约"""
        violator = User.query.filter_by(username='violator').one()
        room = StudyRoom.query.filter_by(name='测试自习室A').one()

        # 准备数据: 一个20分钟前开始但未签到的预约
        now = datetime.utcnow()
        no_show_res = Reservation(
            student_id=violator.id, room_id=room.id, 
            start_time=now - timedelta(minutes=20),
            end_time=now - timedelta(minutes=10),
            status='scheduled'
        )
        session.add(no_show_res)
        session.commit()

        # 执行服务
        ViolationService.process_no_show_violations()
        
        # 验证结果
        assert no_show_res.status == 'violation_no_show'
        student = User.query.get(violator.id)
        assert student.violation_count == 1
        notification = Notification.query.filter_by(user_id=violator.id).first()
        assert notification is not None
        assert "因超时未签到已被取消并记为违约" in notification.message

    def test_process_no_show_violations_bans_user_on_max_violations(self, session):
        """测试达到最大违约次数后，用户应被禁用"""
        violator = User.query.filter_by(username='violator').one()
        room = StudyRoom.query.filter_by(name='测试自习室A').one()
        
        # 准备数据: 学生已有2次违约，再来一次就达到3次
        violator.violation_count = 2
        
        now = datetime.utcnow()
        last_straw_res = Reservation(
            student_id=violator.id, room_id=room.id, 
            start_time=now - timedelta(minutes=30),
            end_time=now - timedelta(minutes=20),
            status='scheduled'
        )
        session.add(last_straw_res)
        session.commit()

        # 执行服务
        ViolationService.process_no_show_violations()

        # 验证结果
        student = User.query.get(violator.id)
        assert student.violation_count == 3
        assert student.banned_until is not None
        assert student.banned_until > now
        
        notification = Notification.query.filter_by(user_id=violator.id).order_by(Notification.id.desc()).first()
        assert "预约功能将被禁用至" in notification.message