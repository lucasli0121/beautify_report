
# General
APP_NAME = "报表美化系统"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Li guo qiang"
LOG_CONTENT = "日志内容"
LOG_STATUS = "状态"
LOG_DATETIME = "时间"
OPERATION = "操作"

HOME_PAGE = "首页"
COMPANY_PAGE = "公司管理"
COMPANY_DETAIL_PAGE = "公司详情"
LOGIN_PAGE = "登录"

string_resources = {
    'app_name': APP_NAME,
    'app_version': APP_VERSION,
    'app_author': APP_AUTHOR,
    'log_content': LOG_CONTENT,
    'log_status': LOG_STATUS,
    'log_datetime': LOG_DATETIME,
    'operation': OPERATION,
    'home_page': HOME_PAGE,
    'company_page': COMPANY_PAGE,
    'company_detail_page': COMPANY_DETAIL_PAGE,
    'login_page': LOGIN_PAGE,
    'brief_report': "财税简报",
    'invoice_title': "发票抬头",
    'invoiced_record': "开票记录",
    'payment_record': "付款记录",
    'paytax_record': "税务记录",
}

def get(key: str) -> str:
    """
    获取字符串资源
    :param key: 字符串资源的键
    :return: 对应的字符串资源
    """
    if key in string_resources:
        return string_resources[key]
    else:
        # 如果键不存在，返回默认值或抛出异常
        # raise KeyError(f"String resource '{key}' not found.")
        # 或者返回键本身作为默认值
        return ""  # 返回空字符串作为默认值