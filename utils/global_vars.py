from nicegui import app
from mq.mq_impl import MqImpl
from db.mydb import MyDb
mq_impl = MqImpl()
my_db = MyDb()

def create_mq() -> bool:
    if mq_impl.connect() is False:
        return False
    mq_impl.loop_for_thread()
    return True

def subscribe_online_topic(mac: str, handle_online_func) -> bool:
    return mq_impl.subscribe(f'hjy-dev/device/heart_beat/{mac.lower()}', handle_online_func)
def unsubscribe_online_topic(mac: str) -> bool:
    return mq_impl.unsubscribe(f'hjy-dev/device/heart_beat/{mac.lower()}')
def subscribe_event_topic(mac: str, handle_event_func) -> bool:
    return mq_impl.subscribe(f'server-h03/study/event/{mac.lower()}', handle_event_func)
def subscribe_attr_topic(mac: str, handle_attr_func) -> bool:
    return mq_impl.subscribe(f'server-t1/study/attr/{mac.lower()}', handle_attr_func)
def unsubscribe_event_topic(mac: str):
    mq_impl.unsubscribe(f'server-h03/study/event/{mac.lower()}')
def unsubscribe_attr_topic(mac: str):
    mq_impl.unsubscribe(f'server-t1/study/attr/{mac.lower()}')