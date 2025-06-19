import pytest
from datetime import datetime, timedelta
from app import create_app
from app.models import User, StudyRoom, Seat, TimeSlot
from app.models import db
from app.services.student_service import StudentService

class TestStudentSearch:

    @pytest.fixture
    def app(self):
        app = create_app('test')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True

        with app.app_context():
            db.create_all()

            # 创建学生
            student = User(
                username='test_student',
                password='password',
                role='student',
                name='测试学生'
            )

            # 创建自习室和座位
            room = StudyRoom(id=1, name='测试自习室', location='测试楼层')
            seat1 = Seat(id=1, seat_number='A1', room_id=1, has_power=True)
            seat2 = Seat(id=2, seat_number='A2', room_id=1, has_power=False)

            db.session.add_all([student, room, seat1, seat2])
            db.session.commit()

        yield app

        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_search_available_seats(self, app):
        """测试搜索可预约座位（无冲突）"""
        with app.app_context():
            start_time = datetime.utcnow() + timedelta(hours=1)
            end_time = start_time + timedelta(hours=1)

            # 不创建 TimeSlot，表示两个座位都空闲
            available = StudentService.search_available_seats(
                room_id=1,
                start=start_time,
                end=end_time,
                require_power=False
            )

            # 断言两个座位都在结果中
            assert len(available) == 2
            assert any(seat["seat_number"] == "A1" for seat in available)
            assert any(seat["seat_number"] == "A2" for seat in available)

    def test_search_available_seats_with_power_filter(self, app):
        """测试只搜索有插座的座位"""
        with app.app_context():
            start_time = datetime.utcnow() + timedelta(hours=1)
            end_time = start_time + timedelta(hours=1)

            available = StudentService.search_available_seats(
                room_id=1,
                start=start_time,
                end=end_time,
                require_power=True
            )

            # 只有 A1 有插座
            assert len(available) == 1
            assert available[0]["seat_number"] == "A1"

    def test_search_excludes_reserved_seats(self, app):
        """测试已被预约的座位不会出现在可预约结果中"""
        with app.app_context():
            # 创建一个 TimeSlot 冲突，表示 A1 已被预约
            reserved_start = datetime.utcnow() + timedelta(hours=1)
            reserved_end = reserved_start + timedelta(hours=2)
            reserved_slot = TimeSlot(
                room_id=1,
                seat_id=1,
                start_time=reserved_start,
                end_time=reserved_end,
                is_reserved=True,
                reserved_by=1
            )
            db.session.add(reserved_slot)
            db.session.commit()

            # 搜索时间和已有预约时间重叠
            search_start = reserved_start + timedelta(minutes=10)
            search_end = search_start + timedelta(minutes=30)

            result = StudentService.search_available_seats(
                room_id=1,
                start=search_start,
                end=search_end,
                require_power=False
            )

            # 只有 A2 可预约
            assert len(result) == 1
            assert result[0]["seat_number"] == "A2"

    def test_search_no_seats(self, app):
        """房间内无座位时，返回空列表"""
        with app.app_context():
            # 删除所有座位
            Seat.query.delete()
            db.session.commit()

            start = datetime.utcnow() + timedelta(hours=1)
            end = start + timedelta(hours=1)

            result = StudentService.search_available_seats(room_id=1, start=start, end=end, require_power=False)
            assert result == []

    def test_search_seat_outside_time_range(self, app):
        """测试预约时间范围无效时，仍返回全部空闲座位"""
        with app.app_context():
            # 设置时间范围，start晚于end，属于无效时间
            start = datetime.utcnow() + timedelta(hours=2)
            end = datetime.utcnow() + timedelta(hours=1)

            # 应该正常返回座位（因为service没有时间逻辑校验）
            result = StudentService.search_available_seats(room_id=1, start=start, end=end, require_power=False)
            assert len(result) == 2  # 两个座位都返回

    def test_search_all_seats_reserved(self, app):
        """测试所有座位均已被预约时，返回空列表"""
        with app.app_context():
            start = datetime.utcnow() + timedelta(hours=1)
            end = start + timedelta(hours=2)

            # 标记所有座位时间段都被预约
            for seat in Seat.query.all():
                slot = TimeSlot(
                    seat_id=seat.id,
                    room_id=seat.room_id,
                    start_time=start,
                    end_time=end,
                    is_reserved=True,
                    reserved_by=1
                )
                db.session.add(slot)
            db.session.commit()

            result = StudentService.search_available_seats(room_id=1, start=start, end=end, require_power=False)
            assert result == []

    def test_search_partial_reserved_seats(self, app):
        """测试部分座位已被预约时，只返回未预约的座位"""
        with app.app_context():
            start = datetime.utcnow() + timedelta(hours=1)
            end = start + timedelta(hours=2)

            # 预约 seat1
            slot = TimeSlot(
                seat_id=1,
                room_id=1,
                start_time=start,
                end_time=end,
                is_reserved=True,
                reserved_by=1
            )
            db.session.add(slot)
            db.session.commit()

            result = StudentService.search_available_seats(room_id=1, start=start, end=end, require_power=False)

            # 只剩 seat2 可预约
            assert len(result) == 1
            assert result[0]['seat_number'] == 'A2'

    def test_search_require_power_true_no_seats(self, app):
        """请求带电源座位，但房间没有带电源座位，返回空列表"""
        with app.app_context():
            # 设置所有座位无电源
            Seat.query.update({Seat.has_power: False})
            db.session.commit()

            start = datetime.utcnow() + timedelta(hours=1)
            end = start + timedelta(hours=1)

            result = StudentService.search_available_seats(room_id=1, start=start, end=end, require_power=True)

            assert result == []

    def test_search_invalid_room(self, app):
        """查询不存在的房间，返回空列表"""
        with app.app_context():
            start = datetime.utcnow() + timedelta(hours=1)
            end = start + timedelta(hours=1)

            result = StudentService.search_available_seats(room_id=999, start=start, end=end, require_power=False)

            assert result == []