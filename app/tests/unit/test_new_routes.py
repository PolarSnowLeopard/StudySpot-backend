import pytest
import json
from datetime import datetime, timedelta
from app import create_app
from app.models.db import db
from app.models import User, StudyRoom, Reservation, Notification, SystemSetting
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='module')
def app():
    app = create_app('test')
    with app.app_context():
        db.create_all()
        admin = User(username='test_admin', password='pw', role='admin', name='测试管理员')
        student = User(username='test_student', password='pw', role='student', name='测试学生')
        room = StudyRoom(name='测试自习室', location='loc')
        
        db.session.add_all([admin, student, room])
        db.session.commit()

        violation_res = Reservation(
            student_id=student.id, room_id=room.id, 
            start_time=datetime.utcnow() - timedelta(days=1),
            end_time=datetime.utcnow() - timedelta(days=1, hours=-1),
            status='violation_no_show'
        )
        noti = Notification(user_id=student.id, message='一条测试通知')
        setting = SystemSetting(key='TEST_KEY', value='test_value', description='desc')

        db.session.add_all([violation_res, noti, setting])
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

@pytest.fixture(scope='module')
def admin_token(app):
    with app.app_context():
        admin = User.query.filter_by(username='test_admin').one()
        return create_access_token(identity=str(admin.id))

@pytest.fixture(scope='module')
def student_token(app):
    with app.app_context():
        student = User.query.filter_by(username='test_student').one()
        return create_access_token(identity=str(student.id))

class TestReservationRoutes:
    def test_get_reservations(self, client, student_token):
        res = client.get('/api/reservations/', headers={'Authorization': f'Bearer {student_token}'})
        data = json.loads(res.data)
        assert res.status_code == 200
        assert data['code'] == 200
        assert len(data['data']) == 1

    def test_get_violation_history(self, client, student_token):
        res = client.get('/api/reservations/violations/history', headers={'Authorization': f'Bearer {student_token}'})
        data = json.loads(res.data)
        assert res.status_code == 200
        assert data['code'] == 200
        assert len(data['data']) == 1
        assert data['data'][0]['status'] == 'violation_no_show'

    def test_get_notifications(self, client, student_token):
        res = client.get('/api/reservations/notifications', headers={'Authorization': f'Bearer {student_token}'})
        data = json.loads(res.data)
        assert res.status_code == 200
        assert data['code'] == 200
        assert len(data['data']) == 1
        assert data['data'][0]['message'] == '一条测试通知'

class TestAdminRoutes:
    def test_get_settings_as_admin(self, client, admin_token):
        res = client.get('/api/admin/settings', headers={'Authorization': f'Bearer {admin_token}'})
        data = json.loads(res.data)
        assert res.status_code == 200
        assert data['code'] == 200
        assert len(data['data']) > 0

    def test_get_settings_as_student_is_forbidden(self, client, student_token):
        res = client.get('/api/admin/settings', headers={'Authorization': f'Bearer {student_token}'})
        data = json.loads(res.data)
        assert res.status_code == 403
        assert data['code'] == 403

    def test_update_settings_as_admin(self, client, admin_token):
        update_data = {'key': 'TEST_KEY', 'value': 'new_value'}
        res = client.post('/api/admin/settings', headers={'Authorization': f'Bearer {admin_token}'}, json=update_data)
        data = json.loads(res.data)
        assert res.status_code == 200
        assert data['code'] == 200
        setting = db.session.get(SystemSetting, 'TEST_KEY')
        assert setting.value == 'new_value'

    def test_get_all_violations_as_admin(self, client, admin_token):
        res = client.get('/api/admin/violations/all', headers={'Authorization': f'Bearer {admin_token}'})
        data = json.loads(res.data)
        assert res.status_code == 200
        assert data['code'] == 200
        assert len(data['data']) == 1
        assert data['data'][0]['student_name'] == '测试学生'