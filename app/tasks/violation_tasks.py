from flask import current_app
from apscheduler.schedulers.background import BackgroundScheduler
from . import ViolationService

def check_and_process_violations():
    """组合任务：检查即将开始的预约和处理违约"""
    with current_app.app_context():
        current_app.logger.info("开始执行违约检查和提醒任务...")
        try:
            # 1. 发送预约开始前提醒
            ViolationService.check_upcoming_reservations()
            
            # 2. 处理超时未签到的违约
            ViolationService.process_no_show_violations()
            
            current_app.logger.info("违约检查和提醒任务执行完毕。")
        except Exception as e:
            current_app.logger.error(f"执行违约检查任务时出错: {e}")

def setup_violation_tasks(app, scheduler):
    """设置违约处理相关的定时任务"""
    # 每分钟执行一次检查
    scheduler.add_job(
        check_and_process_violations,
        'interval',
        minutes=1,
        id='check_violations_job'
    )