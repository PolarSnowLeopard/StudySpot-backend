from datetime import datetime
from flask import current_app
from apscheduler.schedulers.background import BackgroundScheduler
from ..models import StudyRoom, QRCode
from ..services import QRCodeService

# 创建调度器
scheduler = BackgroundScheduler()

def refresh_expired_qrcodes():
    """刷新所有过期的二维码"""
    with current_app.app_context():
        # 获取所有自习室
        rooms = StudyRoom.query.all()
        current_time = datetime.utcnow()
        
        for room in rooms:
            # 获取当前有效的二维码
            qrcode = QRCode.query.filter_by(
                room_id=room.id,
                is_active=True
            ).order_by(QRCode.created_at.desc()).first()
            
            # 如果二维码不存在或已过期，则生成新的
            if not qrcode or current_time >= qrcode.expires_at:
                try:
                    QRCodeService.generate_room_qrcode(room.id)
                    current_app.logger.info(f"已刷新自习室 {room.name} 的二维码")
                except Exception as e:
                    current_app.logger.error(f"刷新自习室 {room.name} 的二维码失败: {str(e)}")

def setup_qrcode_tasks(app):
    """设置二维码相关的定时任务"""
    # 每分钟检查并刷新过期的二维码
    scheduler.add_job(
        refresh_expired_qrcodes,
        'interval',
        minutes=1,
        id='refresh_qrcodes'
    )
    
    # 启动调度器
    scheduler.start()
    
    # 确保应用终止时停止调度器
    import atexit
    atexit.register(lambda: scheduler.shutdown()) 