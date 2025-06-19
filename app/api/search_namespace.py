# 学生查询接口
from app.services.student_service import StudentService
from flask_restx import Namespace, Resource, reqparse
from datetime import datetime


api = Namespace('search', description='学生自助服务')

@api.route('/reservations/<int:student_id>')
class StudentReservations(Resource):
    def get(self, student_id):
        """获取学生预约记录"""
        return StudentService.get_reservation_history(student_id)

# @api.route('/available')
# class AvailableSlots(Resource):
#     def get(self):
#         """获取当前可预约时间块"""
#         return get_available_slots()


@api.route('/room-status')
class RoomSeatStatus(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('room_id', type=int, required=True)
    parser.add_argument('start', type=str, required=True)
    parser.add_argument('end', type=str, required=True)

    def get(self):
        args = self.parser.parse_args()
        room_id = args['room_id']
        start_time = datetime.fromisoformat(args['start'])
        end_time = datetime.fromisoformat(args['end'])

        seat_info = StudentService.get_room_seat_status(room_id, start_time, end_time)

        return {
            "room_id": room_id,
            "start": args['start'],
            "end": args['end'],
            "seats": seat_info
        }


@api.route('/search-available-seats')
class SearchAvailableSeats(Resource):
    def get(self):
        from flask import request

        room_id = int(request.args.get("room_id"))
        start = datetime.fromisoformat(request.args.get("start"))
        end = datetime.fromisoformat(request.args.get("end"))
        has_power = request.args.get("has_power", "false").lower() == "true"

        available_seats = StudentService.search_available_seats(room_id, start, end, has_power)

        return {
            "room_id": room_id,
            "start": request.args.get("start"),
            "end": request.args.get("end"),
            "available_seats": available_seats
        }
