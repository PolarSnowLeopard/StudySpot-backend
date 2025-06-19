from .db import db

class SystemSetting(db.Model):
    """系统配置模型"""
    __tablename__ = 'system_settings'

    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))

    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value,
            'description': self.description
        }