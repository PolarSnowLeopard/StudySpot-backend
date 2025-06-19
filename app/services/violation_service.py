from datetime import datetime, timedelta
from ..models import Reservation, User, SystemSetting, Notification
from app.models.db import db
from flask import current_app

class ViolationService:
    @staticmethod
    def get_setting(key, default_value):
        """获取系统配置"""
        setting = db.session.get(SystemSetting, key)
        if setting:
            try:
                return int(setting.value)
            except (ValueError, TypeError):
                return default_value
        return default_value

    @staticmethod
    def create_notification(user_id, message):
        """为用户创建一条通知"""
        try:
            notification = Notification(user_id=user_id, message=message)
            db.session.add(notification) # <<-- 这里现在是正确的了
            current_app.logger.info(f"为用户 {user_id} 创建通知: {message}")
        except Exception as e:
            current_app.logger.error(f"创建通知失败: {e}")

    @staticmethod
    def check_upcoming_reservations():
        """检查即将开始的预约并发送提醒"""
        # ... (这部分逻辑不变) ...
        reminder_minutes = ViolationService.get_setting('REMINDER_BEFORE_MINUTES', 15)
        now = datetime.utcnow()
        
        upcoming_reservations = Reservation.query.filter(
            Reservation.status == 'scheduled',
            Reservation.start_time > now,
            Reservation.start_time <= now + timedelta(minutes=reminder_minutes)
        ).all()
        
        for res in upcoming_reservations:
            message = f"您的自习室预约即将于 {res.start_time.strftime('%H:%M')} 开始，请准时签到。"
            ViolationService.create_notification(res.student_id, message)
            current_app.logger.info(f"已为预约ID {res.id} 发送开始前提醒。")

    @staticmethod
    def process_no_show_violations():
        """处理超时未签到的违约"""
        # ... (这部分逻辑不变) ...
        timeout_minutes = ViolationService.get_setting('NO_SHOW_TIMEOUT_MINUTES', 10)
        max_violations = ViolationService.get_setting('MAX_VIOLATION_COUNT', 3)
        ban_days = ViolationService.get_setting('BAN_DAYS', 7)
        now = datetime.utcnow()
        
        no_show_reservations = Reservation.query.filter(
            Reservation.status == 'scheduled',
            Reservation.start_time < now - timedelta(minutes=timeout_minutes)
        ).all()
        
        for res in no_show_reservations:
            # 修正点: 使用 session.get
            student = db.session.get(User, res.student_id)
            if not student:
                continue
            
            res.status = 'violation_no_show'
            student.violation_count += 1
            
            if student.violation_count >= max_violations:
                student.banned_until = now + timedelta(days=ban_days)
                ban_end_date = student.banned_until.strftime('%Y-%m-%d')
                message = (f"您的预约（自习室: {res.room.name}, 时间: {res.start_time.strftime('%Y-%m-%d %H:%M')}）"
                           f"因超时未签到已被取消并记为违约。您已累计违约 {student.violation_count} 次，"
                           f"预约功能将被禁用至 {ban_end_date}。")
            else:
                remaining_chances = max_violations - student.violation_count
                message = (f"您的预约（自习室: {res.room.name}, 时间: {res.start_time.strftime('%Y-%m-%d %H:%M')}）"
                           f"因超时未签到已被取消并记为违约。您当前累计违约 {student.violation_count} 次，"
                           f"再违约 {remaining_chances} 次将被禁用预约功能。")
            
            ViolationService.create_notification(student.id, message)
            current_app.logger.info(f"预约ID {res.id} 已被处理为违约。学生ID: {student.id}")

        if no_show_reservations:
            db.session.commit() # <<-- 这里现在是正确的了