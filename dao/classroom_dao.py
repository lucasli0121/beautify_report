from dataclasses import dataclass
from datetime import datetime
import json

import pytz
from api import api_manager


@dataclass
class ClassRoomDao:
    id: int
    name: str
    seat_total_number: int
    seat_row: int
    seat_col: int
    seat_used: int
    create_time: str
    
    def __init__(self, id=0, name="", seat_total_number=0, seat_row=0, seat_col=0, seat_used=0, create_time=""):
        self.id = id
        self.name = name
        self.seat_total_number = seat_total_number
        self.seat_row = seat_row
        self.seat_col = seat_col
        self.seat_used = seat_used
        if create_time == "":
            self.create_time = datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.create_time = create_time
    def from_json(self, json_data):
        self.id = json_data.get('id', 0)
        self.name = json_data.get('name', "")
        self.seat_total_number = json_data.get('seat_total_number', 0)
        self.seat_row = json_data.get('seat_row', 0)
        self.seat_col = json_data.get('seat_col', 0)
        self.seat_used = json_data.get('seat_used', 0)
        self.create_time = json_data.get('create_time', "")
        

    def to_json(self):
        return json.dumps(self.__dict__, default=str)
    
    """
    function:
    description: 从服务器查询教室数据
    param {*} 
    return {*}
    """
    def get_class_room(self):
        url = f"{api_manager.server_url}/classes/queryClassRoomList"
        result = api_manager.api_https.request("GET", url=url, fields=[])
        if result.status == 200:
            jobj = json.loads(result.data)
            if jobj["code"] == 200:
                datas = jobj.get('data', [])
                self.from_json(datas[0])
                return 200, '查询教室成功'
            else:
                return jobj["code"], jobj["message"]
        else:
            return result.status, result.data


@dataclass
class ClassRoomSeatsDao:
    id: int
    class_room_id: int
    is_installed: int
    mac: str
    is_online: int
    seat_no: str
    create_time: str
    
    def __init__(self, id=0, class_room_id=0, is_installed=0, mac="", is_online=0, seat_no="", create_time=""):
        self.id = id
        self.class_room_id = class_room_id
        self.is_installed = is_installed
        self.mac = mac
        self.is_online = is_online
        self.seat_no = seat_no
        if create_time == "":
            self.create_time = datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.create_time = create_time
    def from_json(self, json_data):
        self.id = json_data.get('id', 0)
        self.class_room_id = json_data.get('class_room_id', 0)
        self.is_installed = json_data.get('is_installed', 0)
        self.mac = json_data.get('mac', "")
        self.is_online = json_data.get('is_online', 0)
        self.seat_no = json_data.get('seat_no', "")
        self.create_time = json_data.get('create_time', "")
    def to_json(self):
        return json.dumps(self.__dict__, default=str)
"""
function:
description: 根据教室ID从服务器查询教室座位数据
param {*}
return {*}
"""
def get_class_room_seats_by_classes_id(class_room_id: int) -> tuple[int, str|list[ClassRoomSeatsDao]]:
    return query_class_room_seats_by_condition(class_room_id, "", -1, -1)

"""
function:
description: 根据教室ID和MAC地址从服务器查询教室座位数据
param {*}
return {*}
"""    
def query_class_room_seats_by_condition(class_room_id: int, mac: str, is_installed: int, is_online: int) -> tuple[int, str|list[ClassRoomSeatsDao]]:
    class_room_seats_list = list[ClassRoomSeatsDao]()
    url = f"{api_manager.server_url}/classes/queryClassRoomAndSeats"
    fields = {
        "class_room_id": str(class_room_id),
        "mac": mac,
        "is_installed": str(is_installed),
        "is_online": str(is_online)
    }
    result = api_manager.api_https.request("GET", url=url, fields=fields)
    if result.status == 200:
        jobj = json.loads(result.data)
        if jobj["code"] == 200:
            datas = jobj.get('data', [])
            for item in datas:
                class_room_seats = ClassRoomSeatsDao()
                class_room_seats.from_json(item)
                class_room_seats_list.append(class_room_seats)
            return 200, class_room_seats_list
        else:
            return jobj["code"], jobj["message"]
    else:
        return result.status, str(result.data)    
"""
function:
description: 批量导入设备
param {*} device_list
return {*}
"""
def import_device_to_class_room(device_list: list[ClassRoomSeatsDao]) -> tuple[bool, str]:
    for item in device_list:
        status, result = add_device_to_class_room(item)
        if status is False:
            return status, str(result)
    return True, "导入成功"
"""
function:
description: 向服务器添加设备
param {*} device
return {*}
"""
def add_device_to_class_room(device: ClassRoomSeatsDao) -> tuple[bool, str]:
    url = f"{api_manager.server_url}/classes/installDevices"
    payload = device.to_json()
    status, ret = api_manager.post_to_svr(url, payload)
    if status is False:
        return False, str(ret)
    return True, "添加设备成功"

"""
function:
description: 删除设备
param {*} device
return {*}
"""
def remove_device_from_seats(class_room_id: int, seat_no: str) -> tuple[bool, str]:
    url = f"{api_manager.server_url}/classes/unInstallDevices"
    payload = json.dumps({
        "class_room_id": class_room_id,
        "seat_no": seat_no
    })
    status, ret = api_manager.post_to_svr(url, payload)
    if status is False:
        return False, str(ret)
    return True, "删除设备成功"