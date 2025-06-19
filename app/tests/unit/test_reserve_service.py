import pytest
from datetime import datetime, timedelta
from app import create_app
from app.models import User, StudyRoom, Seat, TimeSlot
from app.models import db
from app.services.student_service import StudentService

class TestStudentReserve:

    @pytest.fixture
    def app(self):
        app = create_app('test')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True

        with app.app_context():
            db.create_all()

            # 创建学生用户
            student = User(
                username='test_student',
                password='password',
                role='student',
                name='测试学生'
            )

            # 创建自习室和座位
            room = StudyRoom(id=2, name='测试自习室', location='测试楼层')
            db.session.add(room)
            db.session.commit()

            # room_id = db.Column(db.Integer, db.ForeignKey('study_room.id'))
            seat = Seat(id=1, room_id=room.id, seat_number='A1', has_power=True)
            db.session.add_all([student, seat])
            db.session.commit()

        yield app

        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_successful_reservation(self, app):
        with app.app_context():
            student = User.query.filter_by(username='test_student').first()
            seat = Seat.query.filter_by(seat_number='A1').first()

            start_time = datetime.utcnow() + timedelta(hours=1)
            end_time = start_time + timedelta(hours=2)

            result = StudentService.reserve_slot(student.id, seat.id, start_time, end_time)

            assert result["success"] is True

    def test_reservation_with_invalid_time(self, app):
        with app.app_context():
            student = User.query.filter_by(username='test_student').first()
            seat = Seat.query.filter_by(seat_number='A1').first()

            start_time = datetime.utcnow() + timedelta(hours=2)
            end_time = start_time - timedelta(hours=1)  # 结束时间早于开始

            result = StudentService.reserve_slot(student.id, seat.id, start_time, end_time)

            assert not result["success"]
            assert "开始时间必须早于结束时间" in result["message"]

    def test_reservation_exceeds_max_duration(self, app):
        with app.app_context():
            student = User.query.filter_by(username='test_student').first()
            seat = Seat.query.filter_by(seat_number='A1').first()

            start_time = datetime.utcnow() + timedelta(hours=1)
            end_time = start_time + timedelta(hours=3)  # 超过2小时

            result = StudentService.reserve_slot(student.id, seat.id, start_time, end_time)

            assert not result["success"]
            assert "不能超过2小时" in result["message"]

    def test_conflict_with_existing_reservation(self, app):
        with app.app_context():
            student = User.query.filter_by(username='test_student').first()
            seat = Seat.query.filter_by(seat_number='A1').first()

            # 创建已有预约
            reserved_slot = TimeSlot(
                seat_id=seat.id,
                room_id=seat.room_id,
                start_time=datetime.utcnow() + timedelta(hours=1),
                end_time=datetime.utcnow() + timedelta(hours=3),
                is_reserved=True,
                reserved_by=999
            )
            db.session.add(reserved_slot)
            db.session.commit()

            # 用户预约重叠时间段
            start_time = datetime.utcnow() + timedelta(hours=2)
            end_time = start_time + timedelta(hours=1)

            result = StudentService.reserve_slot(student.id, seat.id, start_time, end_time)

            assert not result["success"]
            assert "该座位在该时间段已被预约" in result["message"]

    def test_user_has_conflicting_reservation(self, app):
        with app.app_context():
            student = User.query.filter_by(username='test_student').first()
            seat = Seat.query.filter_by(seat_number='A1').first()

            # 模拟学生已有预约
            user_slot = TimeSlot(
                seat_id=seat.id,
                room_id=seat.room_id,
                start_time=datetime.utcnow() + timedelta(hours=1),
                end_time=datetime.utcnow() + timedelta(hours=3),
                is_reserved=True,
                reserved_by=student.id
            )
            db.session.add(user_slot)
            db.session.commit()

            # 预约另一个时间段，但有重叠
            start_time = datetime.utcnow() + timedelta(hours=2)
            end_time = start_time + timedelta(hours=1)

            result = StudentService.reserve_slot(student.id, seat.id, start_time, end_time)

            assert not result["success"]
            assert "该座位在该时间段已被预约" in result["message"]

    def test_reservation_with_invalid_seat_id(self, app):
        with app.app_context():
            student = User.query.filter_by(username='test_student').first()

            start_time = datetime.utcnow() + timedelta(hours=1)
            end_time = start_time + timedelta(hours=2)

            result = StudentService.reserve_slot(student.id, seat_id=999, start_time=start_time, end_time=end_time)

            assert not result["success"]
            assert "座位不存在" in result["message"]
