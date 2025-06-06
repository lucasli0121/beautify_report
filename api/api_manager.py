import json
from typing import Any
import urllib3 as ulib

api_https: ulib.PoolManager
server_url = "http://host.docker.internal:9085/v1"  # Replace with your actual server URL
url_header = {"Content-Type": "application/json"}

"""
function: post_to_svr
description: 实现一个POST方法，向服务器发送POST请求
param {*} self
param {*} url
param {*} payload
return {*}
"""
def post_to_svr(url, payload)-> tuple[bool, Any|str|None]:
    success = False
    ret = None
    global api_https
    try:
        rsp = api_https.request("POST", url, headers=url_header, body=payload)
        if rsp.status == 200:
            jobjs = json.loads(rsp.data)
            if jobjs["code"] == 200:
                success = True
                ret = jobjs["data"]
            else:
                success = False
                ret = str(jobjs["message"])
    except TimeoutError:
        success = False
        ret = "请求超时"
    except ulib.exceptions.SSLError:
        success = False
        ret = "SSL错误"
    except Exception as err:
        success = False
        ret = "请求失败: " + str(err)
    return success, ret
