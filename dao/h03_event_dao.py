from dataclasses import dataclass
from datetime import datetime
import json
from typing import Any
from api import api_manager


@dataclass
class H03EventDao:
    id: int
    mac: str
    body_status: int # 身体状态 有人，无人
    flow_state: int # 0-离开; 1\2\3-浅(活动); 4\5\6-中(学习); 7\8\9-深(心流); 10-异常
    focus_status: int # 学习状态,1: 轻度专注，2: 中度专注，3: 深度专注
    posture_state: int # 0:无人 1:站立 2:端坐 3:趴伏
    activity_freq: int # 0:无人 1:频繁活动 2:轻微活动
    warning_event: int # 1:落座;2:专注度分数低; 3:专注度分数高 4:学习时长超时 5:反复离开 6:坐姿太偏

    def __init__(self, id=0, mac="", body_status=0, flow_state=0, focus_status=0, posture_state=0, activity_freq=0, warning_event=0):
        self.id = id
        self.mac = mac
        self.body_status = body_status
        self.flow_state = flow_state
        self.focus_status = focus_status
        self.posture_state = posture_state
        self.activity_freq = activity_freq
        self.warning_event = warning_event

    def from_json(self, json_data):
        self.id = json_data.get('id', 0)
        self.mac = json_data.get('mac', "")
        self.body_status = json_data.get('body_status', 0)
        self.flow_state = json_data.get('flow_state', 0)
        self.focus_status = json_data.get('focus_status', 0)
        self.posture_state = json_data.get('posture_state', 0)
        self.activity_freq = json_data.get('activity_freq', 0)
        self.warning_event = json_data.get('warning_event', 0)