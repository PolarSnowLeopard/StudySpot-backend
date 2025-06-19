import unittest
from unittest.mock import patch
from flask import Flask
from flask_restx import Api
from app.api.search_namespace import api as search_namespace  # 替换为你实际的文件路径

class SearchApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_namespace(search_namespace, path='/api')
        self.client = self.app.test_client()

    @patch('app.services.student_service.StudentService.get_reservation_history')
    def test_get_student_reservations(self, mock_get_history):
        mock_get_history.return_value = [{"seat_id": 1, "start": "2025-06-19T10:00", "end": "2025-06-19T12:00"}]

        response = self.client.get('/api/reservations/42')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(response.json[0]['seat_id'], 1)

    @patch('app.services.student_service.StudentService.get_room_seat_status')
    def test_room_seat_status(self, mock_room_status):
        mock_room_status.return_value = [
            {"seat_id": 1, "status": "available"},
            {"seat_id": 2, "status": "reserved"},
        ]

        response = self.client.get('/api/room-status', query_string={
            'room_id': 5,
            'start': '2025-06-19T08:00:00',
            'end': '2025-06-19T10:00:00'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('seats', response.json)
        self.assertEqual(len(response.json['seats']), 2)

    @patch('app.services.student_service.StudentService.search_available_seats')
    def test_search_available_seats(self, mock_search_seats):
        mock_search_seats.return_value = [
            {"seat_id": 3, "has_power": True},
            {"seat_id": 4, "has_power": True},
        ]

        response = self.client.get('/api/search-available-seats', query_string={
            'room_id': 3,
            'start': '2025-06-19T14:00:00',
            'end': '2025-06-19T16:00:00',
            'has_power': 'true'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('available_seats', response.json)
        self.assertTrue(response.json['available_seats'][0]['has_power'])

if __name__ == '__main__':
    unittest.main()
