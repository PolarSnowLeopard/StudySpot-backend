# 处理学生侧的核心逻辑，例如搜索可预约时间块等
from typing import List
from app.schemas.search_schema import ReservationOut, AvailableSlot
from app.models import StudyRoom, TimeSlot, Seat
from datetime import datetime, timedelta
from ..models import db

class StudentService:

    @staticmethod
    def get_room_seat_status(room_id: int, start: datetime, end: datetime):
        seats = Seat.query.filter_by(room_id=room_id).all()
        seat_statuses = []

        for seat in seats:
            # 查询该座位在该时间段内是否已被预约
            conflict = TimeSlot.query.filter(
                TimeSlot.seat_id == seat.id,
                TimeSlot.start_time < end,
                TimeSlot.end_time > start,
                TimeSlot.is_reserved == True
            ).first()

            seat_statuses.append({
                "seat_id": seat.id,
                "seat_number": seat.seat_number,
                "has_power": seat.has_power,
                "is_available": conflict is None  # 若无冲突记录，表示可预约
            })

        return seat_statuses

    @staticmethod
    def reserve_slot(user_id: int, seat_id: int, start_time: datetime, end_time: datetime, MAX_RESERVATION_DURATION=timedelta(hours=2)):
        # 校验时间合法
        if start_time >= end_time:
            return {"success": False, "message": "预约开始时间必须早于结束时间"}

        if end_time - start_time > MAX_RESERVATION_DURATION:
            return {"success": False, "message": "预约时长不能超过2小时"}

        # 是否有这个座位
        seat = Seat.query.get(seat_id)
        if not seat:
            return {"success": False, "message": "座位不存在"}

        # 检查该座位是否已被预约（重叠时间）
        conflict = TimeSlot.query.filter(
            TimeSlot.seat_id == seat_id,
            TimeSlot.start_time < end_time,
            TimeSlot.end_time > start_time,
            TimeSlot.is_reserved == True
        ).first()

        if conflict:
            return {"success": False, "message": "该座位在该时间段已被预约"}

        # （可选）用户是否已预约重叠时间段
        user_conflict = TimeSlot.query.filter(
            TimeSlot.reserved_by == user_id,
            TimeSlot.start_time < end_time,
            TimeSlot.end_time > start_time,
            TimeSlot.is_reserved == True
        ).first()

        if user_conflict:
            return {"success": False, "message": "您在该时间段已有预约"}

        # 查找是否已有这个 slot（可精确查 start/end），否则创建新的 TimeSlot
        slot = TimeSlot.query.filter_by(
            room_id=seat.room_id,
            seat_id=seat_id,
            start_time=start_time,
            end_time=end_time
        ).first()

        if not slot:
            # 如果没有现成的时间块，创建新的（也可以不允许）

            slot = TimeSlot(
                seat_id=seat_id,
                room_id=seat.room_id,  # 若 seat 与 room 有关系，可自动填充
                start_time=start_time,
                end_time=end_time
            )
            db.session.add(slot)

        # 执行预约
        slot.is_reserved = True
        slot.reserved_by = user_id
        db.session.commit()

        return {"success": True, "message": "预约成功", "slot_id": slot.id}

    @staticmethod
    def get_reservation_history(user_id: int):
        slots = TimeSlot.query.filter_by(reserved_by=user_id).order_by(TimeSlot.start_time.desc()).all()
        result = []
        for slot in slots:
            seat = Seat.query.get(slot.seat_id)
            room = StudyRoom.query.get(slot.room_id)
            result.append({
                "slot_id": slot.id,
                "room_name": room.name,
                "seat_number": seat.seat_number,
                "start_time": slot.start_time.isoformat(),
                "end_time": slot.end_time.isoformat(),
                "has_ended": slot.end_time < datetime.now()
            })
        return result

    @staticmethod
    def get_quick_recommendation(user_id: int):
        # 简单策略：返回用户上一次预约的座位和时间段
        last_slot = TimeSlot.query.filter_by(reserved_by=user_id).order_by(TimeSlot.start_time.desc()).first()
        if not last_slot:
            return None

        return {
            "seat_id": last_slot.seat_id,
            "room_id": last_slot.room_id,
            "suggested_start_time": last_slot.start_time.replace(day=datetime.now().day).isoformat()
        }

    @staticmethod
    def search_available_seats(room_id: int, start: datetime, end: datetime, require_power: bool = False):
        # 1. 查询该教室中所有座位（可筛选是否带插头）
        seat_query = Seat.query.filter_by(room_id=room_id)
        if require_power:
            seat_query = seat_query.filter_by(has_power=True)
        seats = seat_query.all()

        available = []

        for seat in seats:
            # 2. 查看该座位在给定时间段是否已被预约（存在冲突的 TimeSlot）
            conflict = TimeSlot.query.filter(
                TimeSlot.seat_id == seat.id,
                TimeSlot.start_time < end,
                TimeSlot.end_time > start,
                TimeSlot.is_reserved == True
            ).first()

            if conflict is None:
                available.append({
                    "seat_id": seat.id,
                    "seat_number": seat.seat_number,
                    "has_power": seat.has_power
                })

        return available

    @staticmethod
    def get_student_reservations(student_id: int) -> List[ReservationOut]:
        # 这里你可以用 ORM 查询 student_id 对应的预约记录
        return []  # 返回 ReservationOut 列表
#
# def get_available_slots() -> List[AvailableSlot]:
#     # 查询所有当前可用座位、时间段
#     return []  # 返回 AvailableSlot 列表
#
# def get_current_reservation_count(TimeSlot, room_id):
#     """查询某时间段、某教室的已有预约数"""
#     start, end = TimeSlot
#     return Reservation.query.filter(
#         Reservation.room_id == room_id,
#         Reservation.start_time >= start,
#         Reservation.end_time <= end
#     ).count()
