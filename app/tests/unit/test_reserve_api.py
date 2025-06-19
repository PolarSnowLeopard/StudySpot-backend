import unittest
from unittest.mock import patch
from flask import Flask
from flask_restx import Api
from app.api.reserve_namespace import api as reserve_namespace  # 导入你的 namespace

class ReserveSeatTestCase(unittest.TestCase):
    def setUp(self):
        # 创建 Flask 测试应用
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_namespace(reserve_namespace, path='/api')
        self.client = self.app.test_client()

    @patch('app.services.student_service.StudentService.reserve_slot')
    def test_successful_reservation(self, mock_reserve_slot):
        mock_reserve_slot.return_value = {
            'success': True,
            'message': 'Reservation successful'
        }

        payload = {
            'user_id': 1,
            'seat_id': 10,
            'start_time': '2025-06-19T10:00:00',
            'end_time': '2025-06-19T12:00:00'
        }

        response = self.client.post('/api/reserve-seat', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json)
        self.assertTrue(response.json['success'])

    @patch('app.services.student_service.StudentService.reserve_slot')
    def test_failed_reservation(self, mock_reserve_slot):
        mock_reserve_slot.return_value = {
            'success': False,
            'message': 'Seat already reserved'
        }

        payload = {
            'user_id': 1,
            'seat_id': 10,
            'start_time': '2025-06-19T10:00:00',
            'end_time': '2025-06-19T12:00:00'
        }

        response = self.client.post('/api/reserve-seat', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('success', response.json)
        self.assertFalse(response.json['success'])

if __name__ == '__main__':
    unittest.main()
