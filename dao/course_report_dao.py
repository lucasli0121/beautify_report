from dataclasses import dataclass
from datetime import datetime
import json
from typing import Any
from api import api_manager


@dataclass
class ConcentrationTrade:
    low_concentration_num: int
    mid_concentration_num: int
    deep_concentration_num: int
    create_time: str
    def __init__(self, low_concentration_num=0, mid_concentration_num=0, deep_concentration_num=0, create_time=""):
        self.low_concentration_num = low_concentration_num
        self.mid_concentration_num = mid_concentration_num
        self.deep_concentration_num = deep_concentration_num
        if create_time == "":
            self.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.create_time = create_time
    def from_json(self, json_data):
        self.low_concentration_num = json_data.get('low_concentration_num', 0)
        self.mid_concentration_num = json_data.get('mid_concentration_num', 0)
        self.deep_concentration_num = json_data.get('deep_concentration_num', 0)
        self.create_time = json_data.get('create_time', "")

@dataclass
class ConcentrationDistribution:
    less_than_10_min_num: int
    less_than_20_min_num: int
    less_than_30_min_num: int
    greater_than_30_min_num: int
    def __init__(self, less_than_10_min_num=0, less_than_20_min_num=0, less_than_30_min_num=0, greater_than_30_min_num=0):
        self.less_than_10_min_num = less_than_10_min_num
        self.less_than_20_min_num = less_than_20_min_num
        self.less_than_30_min_num = less_than_30_min_num
        self.greater_than_30_min_num = greater_than_30_min_num
    def from_json(self, json_data):
        self.less_than_10_min_num = json_data.get('less_than_10_min_num', 0)
        self.less_than_20_min_num = json_data.get('less_than_20_min_num', 0)
        self.less_than_30_min_num = json_data.get('less_than_30_min_num', 0)
        self.greater_than_30_min_num = json_data.get('greater_than_30_min_num', 0)

@dataclass
class CourseReportDao:
    class_room_id: int
    course_id: int
    concentration_trade: list[ConcentrationTrade]
    mid_concentration_distribution: ConcentrationDistribution
    deep_concentration_distribution: ConcentrationDistribution

    def __init__(self, class_room_id=0, course_id=0, concentration_trade=None):
        self.class_room_id = class_room_id
        self.course_id = course_id
        if concentration_trade is None:
            self.concentration_trade = []
        else:
            self.concentration_trade = concentration_trade
        self.mid_concentration_distribution = ConcentrationDistribution()
        self.deep_concentration_distribution = ConcentrationDistribution()

    def from_json(self, json_data):
        self.class_room_id = json_data.get('class_room_id', 0)
        self.course_id = json_data.get('course_id', 0)
        concentration_trade_list = json_data.get('concentration_trade', [])
        self.concentration_trade = []
        if concentration_trade_list is not None:
            for concentration_trade in concentration_trade_list:
                concentration_trade_obj = ConcentrationTrade()
                concentration_trade_obj.from_json(concentration_trade)
                self.concentration_trade.append(concentration_trade_obj)
        mid_concentration_distribution = json_data.get('mid_concentration_distribution', {})
        self.mid_concentration_distribution.from_json(mid_concentration_distribution)
        deep_concentration_distribution = json_data.get('deep_concentration_distribution', {})
        self.deep_concentration_distribution.from_json(deep_concentration_distribution)

#
# Function to get course report by class room id and course id
# @param class_room_id: class room id
# @param course_id: course id
# @return: tuple of status code and course report dao object or error message
# @rtype: tuple[int, str|CourseReportDao]
#
def get_course_report_by_course_id(class_room_id: int, course_id: int) -> tuple[int, str|CourseReportDao]:
    url = f"{api_manager.server_url}/course/queryCourseReport"
    fields = { 
        "class_room_id": str(class_room_id), \
        "course_id": str(course_id) \
        }
    result = api_manager.api_https.request("GET", url=url, fields=fields)
    if result.status == 200:
        jobj = json.loads(result.data)
        if jobj["code"] == 200:
            datas = jobj.get('data', {})
            course_report_dao = CourseReportDao()
            course_report_dao.from_json(datas)
            return 200, course_report_dao
        else:
            return jobj["code"], jobj["message"]
    else:
        return result.status, str(result.data)
    
@dataclass
class CourseStudentsConcentrationDao:
    course_id: int
    student_id: int
    name: str
    gender: int
    low_concentration: float
    mid_concentration: float
    deep_concentration: float
    total_concentration: int

    def __init__(self, course_id=0, student_id=0, name="", gender=0, low_concentration=0, mid_concentration=0, deep_concentration=0, total_concentration=0):
        self.course_id = course_id
        self.student_id = student_id
        self.name = name
        self.gender = gender
        self.low_concentration = low_concentration
        self.mid_concentration = mid_concentration
        self.deep_concentration = deep_concentration
        self.total_concentration = total_concentration
    def from_json(self, json_data):
        self.course_id = json_data.get('course_id', 0)
        self.student_id = json_data.get('student_id', 0)
        self.name = json_data.get('name', "")
        self.gender = json_data.get('gender', 0)
        self.low_concentration = json_data.get('low_concentration', 0.0)
        self.mid_concentration = json_data.get('mid_concentration', 0.0)
        self.deep_concentration = json_data.get('deep_concentration', 0.0)
        self.total_concentration = json_data.get('total_concentration', 0)


#
# Function to query course student concentration by course id
# @param course_id: course id
# @return: tuple of status code and list of course students concentration dao objects or error message
# @rtype: tuple[int, str|list[CourseStudentsConcentrationDao]]
#
def query_course_student_concentration(course_id: int) -> tuple[int, str|list[CourseStudentsConcentrationDao]]:
    url = f"{api_manager.server_url}/course/queryCourseStudentConcentration"
    fields = { 
        "course_id": str(course_id) \
    }
    course_students_concentration_list = []
    result = api_manager.api_https.request("GET", url=url, fields=fields)
    if result.status == 200:
        jobj = json.loads(result.data)
        if jobj["code"] == 200:
            datas = jobj.get('data', {})
            for item in datas:
                course_students_concentration_dao = CourseStudentsConcentrationDao()
                course_students_concentration_dao.from_json(item)
                course_students_concentration_list.append(course_students_concentration_dao)
            return 200, course_students_concentration_list
        else:
            return jobj["code"], jobj["message"]
    return result.status, str(result.data)