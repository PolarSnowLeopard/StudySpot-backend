# 学生相关接口的数据模型，如查询结果、取消请求参数等

from pydantic import BaseModel
from datetime import datetime, time

class ReservationOut(BaseModel):
    room_id: int
    seat_id: int
    start_time: time
    end_time: time
    status: str

class AvailableSlot(BaseModel):
    room_id: int
    seat_id: int
    available_from: datetime
    available_to: datetime
