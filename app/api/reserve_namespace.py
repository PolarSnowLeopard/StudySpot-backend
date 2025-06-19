from flask_restx import Namespace, Resource
from flask import request
from datetime import datetime
from app.services.student_service import StudentService

api = Namespace('reserve', description='学生预约接口')

@api.route('/reserve-seat')
class ReserveSeat(Resource):
    def post(self):
        data = request.get_json()
        user_id = data['user_id']
        seat_id = data['seat_id']
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = datetime.fromisoformat(data['end_time'])

        result = StudentService.reserve_slot(user_id, seat_id, start_time, end_time)
        status_code = 200 if result['success'] else 400
        return result, status_code
