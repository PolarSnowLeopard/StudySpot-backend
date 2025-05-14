from datetime import datetime, timedelta
import json
import base64
import hmac
import hashlib
from ..models import StudyRoom, QRCode
from ..models.db import db

class QRCodeService:
    # 用于签名的密钥，实际应用中应从配置中读取
    SECRET_KEY = 'study_spot_qrcode_secret_key'
    
    @staticmethod
    def generate_signature(data):
        """生成数据签名"""
        # 将数据转换为字符串
        data_str = json.dumps(data, sort_keys=True)
        # 使用HMAC-SHA256生成签名
        signature = hmac.new(
            QRCodeService.SECRET_KEY.encode(),
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    @staticmethod
    def verify_signature(data, signature):
        """验证数据签名"""
        computed_signature = QRCodeService.generate_signature(data)
        return computed_signature == signature
    
    @staticmethod
    def generate_room_qrcode(room_id):
        """为指定自习室生成新的二维码
        
        Args:
            room_id: 自习室ID
            
        Returns:
            dict: 包含二维码信息的字典
        """
        # 检查自习室是否存在
        room = StudyRoom.query.get_or_404(room_id)
        
        # 生成唯一编码
        unique_code = QRCode.generate_code()
        
        # 设置过期时间
        expires_at = datetime.utcnow() + timedelta(minutes=room.qrcode_refresh_interval)
        
        # 将旧的二维码设为失效
        old_qrcodes = QRCode.query.filter_by(room_id=room_id, is_active=True).all()
        for old_qrcode in old_qrcodes:
            old_qrcode.is_active = False
        
        # 创建新的二维码记录
        qrcode = QRCode(
            room_id=room_id,
            code=unique_code,
            expires_at=expires_at,
            is_active=True
        )
        
        db.session.add(qrcode)
        db.session.commit()
        
        # 生成二维码数据
        qrcode_data = {
            'room_id': room_id,
            'code': unique_code,
            'expires_at': expires_at.isoformat()
        }
        
        # 添加签名
        signature = QRCodeService.generate_signature(qrcode_data)
        
        # 返回完整的二维码数据
        return {
            'data': qrcode_data,
            'signature': signature,
            'qrcode_id': qrcode.id
        }
    
    @staticmethod
    def get_active_qrcode(room_id):
        """获取自习室当前有效的二维码
        
        Args:
            room_id: 自习室ID
            
        Returns:
            dict: 包含二维码信息的字典，如果没有有效二维码则生成新的
        """
        # 查找当前有效的二维码
        qrcode = QRCode.query.filter_by(
            room_id=room_id,
            is_active=True
        ).order_by(QRCode.created_at.desc()).first()
        
        # 如果没有有效二维码或二维码已过期，则生成新的
        if not qrcode or qrcode.is_expired():
            return QRCodeService.generate_room_qrcode(room_id)
        
        # 生成二维码数据
        qrcode_data = {
            'room_id': room_id,
            'code': qrcode.code,
            'expires_at': qrcode.expires_at.isoformat()
        }
        
        # 添加签名
        signature = QRCodeService.generate_signature(qrcode_data)
        
        # 返回完整的二维码数据
        return {
            'data': qrcode_data,
            'signature': signature,
            'qrcode_id': qrcode.id
        }
    
    @staticmethod
    def encode_qrcode_for_display(qrcode_data):
        """将二维码数据编码为适合显示的格式
        
        Args:
            qrcode_data: 二维码数据字典
            
        Returns:
            str: Base64编码的二维码字符串
        """
        # 将二维码数据转换为JSON字符串
        json_data = json.dumps(qrcode_data)
        
        # Base64编码
        encoded_data = base64.b64encode(json_data.encode()).decode()
        
        return encoded_data
    
    @staticmethod
    def decode_qrcode(encoded_data):
        """解码二维码数据
        
        Args:
            encoded_data: Base64编码的二维码字符串
            
        Returns:
            dict: 二维码数据字典
        """
        try:
            # Base64解码
            json_data = base64.b64decode(encoded_data.encode()).decode()
            
            # 解析JSON
            qrcode_data = json.loads(json_data)
            
            return qrcode_data
        except Exception as e:
            return None
    
    @staticmethod
    def verify_qrcode(encoded_data):
        """验证二维码有效性
        
        Args:
            encoded_data: Base64编码的二维码字符串
            
        Returns:
            tuple: (是否有效, 错误消息, 二维码对象)
        """
        # 解码二维码数据
        qrcode_data = QRCodeService.decode_qrcode(encoded_data)
        if not qrcode_data:
            return False, "无效的二维码格式", None
        
        # 验证签名
        signature = qrcode_data.get('signature')
        data = qrcode_data.get('data')
        
        if not signature or not data:
            return False, "二维码数据不完整", None
        
        if not QRCodeService.verify_signature(data, signature):
            return False, "二维码验证失败，可能已被篡改", None
        
        # 获取二维码信息
        room_id = data.get('room_id')
        code = data.get('code')
        expires_at_str = data.get('expires_at')
        
        if not all([room_id, code, expires_at_str]):
            return False, "二维码数据缺失", None
        
        # 转换过期时间
        try:
            expires_at = datetime.fromisoformat(expires_at_str)
        except ValueError:
            return False, "二维码格式错误", None
        
        # 检查是否过期
        if datetime.utcnow() > expires_at:
            return False, "二维码已过期", None
        
        # 验证二维码是否存在且有效
        qrcode = QRCode.query.filter_by(
            room_id=room_id,
            code=code,
            is_active=True
        ).first()
        
        if not qrcode:
            return False, "无效的二维码", None
        
        # 所有验证通过
        return True, None, qrcode 