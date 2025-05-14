from datetime import datetime
from flask_jwt_extended import get_jwt_identity
from ..models import User, StudyRoom, QRCode, CheckIn
from ..models.db import db
from .qrcode_service import QRCodeService

class CheckInService:
    @staticmethod
    def student_check_in(student_id, encoded_qrcode):
        """学生签到
        
        Args:
            student_id: 学生ID
            encoded_qrcode: 编码后的二维码字符串
            
        Returns:
            dict: 包含签到结果的字典
        """
        try:
            # 验证二维码
            is_valid, error_msg, qrcode = QRCodeService.verify_qrcode(encoded_qrcode)
            
            if not is_valid:
                return {
                    'success': False,
                    'message': error_msg
                }
            
            # 获取自习室信息
            room_id = qrcode.room_id
            
            # 检查学生是否已经在该自习室签到
            existing_check_in = CheckIn.query.filter_by(
                student_id=student_id,
                room_id=room_id,
                status='checked_in'
            ).first()
            
            if existing_check_in:
                return {
                    'success': False,
                    'message': '您已经在该自习室签到'
                }
            
            # 获取自习室信息
            room = StudyRoom.query.get(room_id)
            if not room:
                return {
                    'success': False,
                    'message': '自习室不存在'
                }
            
            # 创建新的签到记录
            check_in = CheckIn(
                student_id=student_id,
                room_id=room_id,
                qrcode_id=qrcode.id,
                status='checked_in',
                check_in_time=datetime.utcnow()
            )
            
            db.session.add(check_in)
            db.session.commit()
            
            # 返回签到成功信息
            return {
                'success': True,
                'message': '签到成功',
                'data': {
                    'check_in_id': check_in.id,
                    'room_name': room.name,
                    'room_location': room.location,
                    'check_in_time': check_in.check_in_time.isoformat()
                }
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'签到失败: {str(e)}'
            }
    
    @staticmethod
    def student_check_out(student_id, room_id):
        """学生签退
        
        Args:
            student_id: 学生ID
            room_id: 自习室ID
            
        Returns:
            dict: 包含签退结果的字典
        """
        try:
            # 查找学生在该自习室的最新签到记录
            check_in = CheckIn.query.filter_by(
                student_id=student_id,
                room_id=room_id,
                status='checked_in'
            ).order_by(CheckIn.check_in_time.desc()).first()
            
            if not check_in:
                return {
                    'success': False,
                    'message': '未找到有效的签到记录'
                }
            
            # 更新签退信息
            check_in.status = 'checked_out'
            check_in.check_out_time = datetime.utcnow()
            
            # 计算学习时长
            check_in.duration = check_in.calculate_duration()
            
            db.session.commit()
            
            # 返回签退成功信息
            return {
                'success': True,
                'message': '签退成功',
                'data': {
                    'check_in_id': check_in.id,
                    'duration': check_in.duration,
                    'check_out_time': check_in.check_out_time.isoformat()
                }
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'签退失败: {str(e)}'
            }
    
    @staticmethod
    def get_student_check_ins(student_id, status=None, limit=10, offset=0):
        """获取学生的签到记录
        
        Args:
            student_id: 学生ID
            status: 签到状态过滤
            limit: 记录数量限制
            offset: 记录偏移量
            
        Returns:
            list: 签到记录列表
        """
        try:
            # 构建查询
            query = CheckIn.query.filter_by(student_id=student_id)
            
            # 应用状态过滤
            if status:
                query = query.filter_by(status=status)
            
            # 排序并分页
            check_ins = query.order_by(
                CheckIn.check_in_time.desc()
            ).limit(limit).offset(offset).all()
            
            # 转换为字典列表
            result = []
            for check_in in check_ins:
                # 获取关联信息
                room = StudyRoom.query.get(check_in.room_id)
                
                # 构建记录字典
                record = check_in.to_dict()
                record['room_name'] = room.name if room else '未知'
                record['room_location'] = room.location if room else '未知'
                
                result.append(record)
            
            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'获取签到记录失败: {str(e)}'
            } 