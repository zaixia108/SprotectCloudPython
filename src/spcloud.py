from ctypes import *
import ctypes
import os


sp = ctypes.WinDLL(os.path.join(os.path.dirname(__file__), 'SPCloud64_Py.dll'))


class TagPCSignInfo(Structure):
    _pack_ = 1
    _fields_ = [
        ("u64BindTS", c_ulonglong),  # 绑定时间戳
        ("szWinVer", c_char_p),      # 操作系统版本
        ("szRemark", c_char_p),      # 备注
        ("szComputerName", c_char_p),# 计算机名
        ("szPCSign", c_char_p),      # 机器码
        ("u64LastLoginTS", c_ulonglong),  # 最后登录时间
        ("Reserved", c_void_p * 20)  # 保留字段
    ]

class TagPCSignInfoHead(Structure):
    _pack_ = 1
    _fields_ = [
        ("u32Count", c_uint),                      # 信息数量
        ("Info", POINTER(TagPCSignInfo)),         # 指向 TagPCSignInfo 数组的指针
        ("u32BindIP", c_uint),                     # 是否绑定IP
        ("u32RestCount", c_uint),                  # 周期内剩余次数
        ("u64RefreshCountdownSeconds", c_ulonglong),  # 更新倒计时的秒数
        ("u32Limit", c_uint),                      # 限制解绑
        ("Reserved", c_void_p * 19)      # 保留字段
    ]

class TagOnlineInfo(Structure):
    _pack_ = 1
    _fields_ = [
        ("u32CID", c_uint),
        ("szComputerName", c_char_p),
        ("szWinVer", c_char_p),
        ("u64CloudInitTS", c_ulonglong),
        ("Reserved", c_void_p * 20)
    ]

class TagOnlineInfoHead(Structure):
    _pack_ = 1
    _fields_ = [
        ("u32Count", c_uint),
        ("Info", POINTER(TagOnlineInfo)),
        ("Reserved", c_void_p * 20)
    ]

class TagUserRechargedInfo(Structure):
    _pack_ = 1  # 设置为 1 字节对齐
    _fields_ = [
        ("u64OldExpiredTimeStamp", c_ulonglong),  # 旧的过期时间戳
        ("u64NewExpiredTimeStamp", c_ulonglong),  # 新的过期时间戳
        ("u64OldFYI", c_ulonglong),                # 旧的点数
        ("u64NewFYI", c_ulonglong),                # 新的点数
        ("u32RechargeCount", c_uint),              # 本次充值的卡密个数
        ("Reserved", c_void_p * 80)      # 保留字段
    ]

class TagBasicInfo(Structure):
    _fields_ = [
        ("ForbidTrial", c_uint),
        ("ForbidLogin", c_uint),
        ("ForbidRegister", c_uint),
        ("ForbidRecharge", c_uint),
        ("ForbidCloudGetCountinfo", c_uint),
        ("Reserved", c_uint * 15)
    ]


def sp_cloud_create():
    """
    描述: 云计算, 创建一个云计算对象 , 后续cloud都是这个对象
    :return:
    """
    sp.SP_Cloud_Create.restype = c_void_p
    return sp.SP_Cloud_Create()


def sp_card_login(cloud, card: str):
    """
    /* 描述: SP云计算_登录; 不可与SP_CloudInit函数一起使用! */
    :param cloud:
    :param card: 卡密
    :return: bool
    """
    error_code = c_int()
    sp.SP_CloudLogin.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
    sp.SP_CloudLogin.restype = c_bool
    card = bytes(card, 'gbk')
    ret = sp.SP_CloudLogin(cloud, card, byref(error_code))
    return {'ret': ret, 'code': error_code.value}


def sp_user_login(cloud, user: str, password: str):
    """
    /* 描述: SP云计算_登录; 不可与SP_CloudInit函数一起使用! */
    :param cloud:
    :param user: 用户名
    :param password: 密码
    :return: bool
    """
    error_code = c_int()
    sp.SP_CloudUserLogin.argtypes = [c_void_p, c_char_p, c_char_p, POINTER(c_int)]
    sp.SP_CloudUserLogin.restype = c_bool
    user = bytes(user, 'gbk')
    password = bytes(password, 'gbk')
    ret = sp.SP_CloudUserLogin(cloud, user, password, byref(error_code))
    return {'ret': ret, 'code': error_code.value}


def sp_cloud_set_conninfo(cloud, software_name: str, ip: str, port: int, timeout: int,
                          localversion: int, pop_out: c_bool):
    """
    /* 描述: SP云计算_设置连接信息; 不可与SP_CloudInit函数一起使用! */
    :param localversion:
    :param cloud:
    :param software_name: 软件名称
    :param ip: IP地址
    :param port: 端口
    :param timeout: 超时时间
    :param pop_out: 是否弹窗
    :return: bool
    """
    software_name = bytes(software_name, 'gbk')
    sp.SP_CloudSetConnInfo.argtypes = [c_void_p, c_char_p, c_char_p, c_int, c_int, c_int, c_bool]
    ip = bytes(ip, 'gbk')
    sp.SP_CloudSetConnInfo(cloud, software_name, ip, port, timeout, localversion, pop_out)
    return None


def sp_cloud_computing(cloud, cloud_id: int , in_buffer, in_length, retry_count=0, retry_interval_ms=0):
    """
    /* 描述: 云计算请求 (每次调用联网) */
    /* 该函数返回true时, pOutBuffer若不为0, 则需要用户自己释放内存 SP_Cloud_Free(pOutBuffer) */
    :param cloud:
    :param cloud_id: 云计算ID
    :param in_buffer: 云计算数据包指针
    :param in_length: 云计算数据包长度
    :param retry_count: 重试次数
    :param retry_interval_ms: 重试间隔
    :return: bool
    """
    sp.SP_CloudComputing.argtypes = [c_void_p, c_int, POINTER(c_uint), c_uint, POINTER(POINTER(c_uint)), POINTER(c_uint), POINTER(c_int), c_uint, c_uint]
    sp.SP_CloudComputing.restype = c_bool
    out_length = c_uint()
    out_buffer = POINTER(c_uint)()
    error_code = c_int()
    ret = sp.SP_CloudComputing(cloud, cloud_id, in_buffer, in_length, byref(out_buffer), byref(out_length), byref(error_code), retry_count, retry_interval_ms)
    return {'ret': ret, 'out_buffer': out_buffer, 'out_length': out_length.value, 'code': error_code.value}


def sp_cloud_beat(cloud):
    """
    /* 描述: 云计算, 频率验证 (每次调用联网; 建议创建一条线程来频繁调用, 比如30秒调用一次) */
    :param cloud:
    :return: bool
    """
    sp.SP_Cloud_Beat.argtypes = [c_void_p, POINTER(c_int)]
    sp.SP_Cloud_Beat.restype = c_bool
    error_code = c_int()
    ret = sp.SP_Cloud_Beat(cloud, byref(error_code))
    return {'ret': ret, 'code': error_code.value}


def sp_cloud_get_card_agent(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密所属代理名 (每次调用联网) */
    :param cloud:
    :return: bool, 代理名
    """
    sp.SP_Cloud_GetCardAgent.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
    sp.SP_Cloud_GetCardAgent.restype = c_bool
    sz_agent = create_string_buffer(44)
    error_code = c_int()
    ret = sp.SP_Cloud_GetCardAgent(cloud, sz_agent, byref(error_code))
    return {'ret': ret, 'agent': sz_agent.value.decode('gbk'), 'code': error_code.value}


def sp_cloud_get_card_type(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密的卡类型 (每次调用联网) */
    :param cloud:
    :return: bool, 卡密类型
    """
    sp.SP_Cloud_GetCardType.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
    sp.SP_Cloud_GetCardType.restype = c_bool
    error_code = c_int()
    card_type = create_string_buffer(36)
    ret = sp.SP_Cloud_GetCardType(cloud, card_type, byref(error_code))
    return {'ret': ret,'card_type':card_type.value.decode('gbk') , 'code': error_code.value}


def sp_cloud_get_ip_address(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密登录时记录的IP地址 (每次调用联网) */
    :param cloud:
    :return: bool, IP地址
    """
    sp.SP_Cloud_GetIPAddress.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
    sp.SP_Cloud_GetIPAddress.restype = c_bool
    error_code = c_int()
    ip_address = create_string_buffer(44)
    ret = sp.SP_Cloud_GetIPAddress(cloud, ip_address, byref(error_code))
    return {'ret': ret, 'ip_address': ip_address.value.decode('gbk'), 'code': error_code.value}


def sp_cloud_get_remarks(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密的备注 (每次调用联网) */
    :param cloud:
    :return: bool, 备注
    """
    sp.SP_Cloud_GetRemarks.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
    sp.SP_Cloud_GetRemarks.restype = c_bool
    error_code = c_int()
    remarks = create_string_buffer(132)
    ret = sp.SP_Cloud_GetRemarks(cloud, remarks, byref(error_code))
    return {'ret': ret, 'remarks': remarks.value.decode('gbk'), 'code': error_code.value}


def sp_cloud_get_created_time_stamp(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密的创建时间戳 (每次调用联网) */
    :param cloud:
    :return: bool, 创建时间戳
    """
    sp.SP_Cloud_GetCreatedTimeStamp.argtypes = [c_void_p, POINTER(c_longlong), POINTER(c_int)]
    sp.SP_Cloud_GetCreatedTimeStamp.restype = c_bool
    created_time_stamp = c_longlong()
    error_code = c_int()
    ret = sp.SP_Cloud_GetCreatedTimeStamp(cloud, byref(created_time_stamp), byref(error_code))

    return {'ret': ret, 'created_time_stamp': created_time_stamp.value, 'code': error_code.value}


def sp_cloud_get_activated_time_stamp(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密的激活时间戳 (每次调用联网) */
    :param cloud:
    :return: bool, 激活时间戳
    """
    sp.SP_Cloud_GetActivatedTimeStamp.argtypes = [c_void_p, POINTER(c_ulonglong), POINTER(c_int)]
    sp.SP_Cloud_GetActivatedTimeStamp.restype = c_bool
    error_code = c_int()
    activated_time_stamp = c_ulonglong()
    ret = sp.SP_Cloud_GetActivatedTimeStamp(cloud, byref(activated_time_stamp), byref(error_code))
    return {'ret': ret, 'activated_time_stamp': activated_time_stamp.value, 'code': error_code.value}


def sp_cloud_get_expired_time_stamp(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密的过期时间戳 (每次调用联网) */
    :param cloud:
    :return: bool, 过期时间戳
    """
    sp.SP_Cloud_GetExpiredTimeStamp.argtypes = [c_void_p, POINTER(c_ulonglong), POINTER(c_int)]
    sp.SP_Cloud_GetExpiredTimeStamp.restype = c_bool
    error_code = c_int()
    expired_time_stamp = c_ulonglong()
    ret = sp.SP_Cloud_GetExpiredTimeStamp(cloud, byref(expired_time_stamp), byref(error_code))
    return {'ret': ret, 'expired_time_stamp': expired_time_stamp.value, 'code': error_code.value}


def sp_cloud_get_last_login_time_stamp(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密的最后登录时间戳 (每次调用联网) */
    :param cloud:
    :return: bool, 最后登录时间戳
    """
    sp.SP_Cloud_GetLastLoginTimeStamp.argtypes = [c_void_p, POINTER(c_ulonglong), POINTER(c_int)]
    sp.SP_Cloud_GetLastLoginTimeStamp.restype = c_bool
    error_code = c_int()
    last_login_time_stamp = c_ulonglong()
    ret = sp.SP_Cloud_GetLastLoginTimeStamp(cloud, byref(last_login_time_stamp), byref(error_code))
    return {'ret': ret, 'last_login_time_stamp': last_login_time_stamp.value, 'code': error_code.value}


def sp_cloud_get_fyi(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密的剩余点数 (每次调用联网) */
    :param cloud:
    :return: bool, 剩余点数
    """
    sp.SP_Cloud_GetFYI.argtypes = [c_void_p, POINTER(c_longlong), POINTER(c_int)]
    sp.SP_Cloud_GetFYI.restype = c_bool
    fyi = c_longlong()
    error_code = c_int()
    ret = sp.SP_Cloud_GetFYI(cloud, byref(fyi), byref(error_code))

    return {'ret': ret, 'fyi': fyi.value, 'code': error_code.value}


def sp_cloud_deduct_fyi(cloud, fyi_count):
    """
    /* 描述: 扣除当前卡密点数; 用于用户使用了某些特殊功能需要额外扣费的场景 (每次调用联网) */
    :param cloud:
    :param fyi_count: 扣点数量
    :return: bool
    """
    sp.SP_Cloud_DeductFYI.argtypes = [c_void_p, c_ulonglong, POINTER(c_ulonglong), POINTER(c_int)]
    sp.SP_Cloud_DeductFYI.restype = c_bool
    error_code = c_int()
    surplus_fyi = c_ulonglong()
    ret = sp.SP_Cloud_DeductFYI(cloud, fyi_count, byref(surplus_fyi), byref(error_code))
    return {'ret': ret, 'code': error_code.value}


def sp_cloud_get_open_max_num(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密的多开数量属性值 (每次调用联网) */
    :param cloud:
    :return: bool, 多开数量
    """
    sp.SP_Cloud_GetOpenMaxNum.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
    sp.SP_Cloud_GetOpenMaxNum.restype = c_bool
    num = c_int()
    error_code = c_int()
    ret = sp.SP_Cloud_GetOpenMaxNum(cloud, byref(num), byref(error_code))

    return {'ret': ret, 'num': num.value, 'code': error_code.value}


def sp_cloud_get_bind(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密的绑定机器属性值 (每次调用联网) */
    :param cloud:
    :return: bool, 绑定机器属性
    """
    sp.SP_Cloud_GetBind.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
    sp.SP_Cloud_GetBind.restype = c_bool
    bind = c_int()
    error_code = c_int()
    result = sp.SP_Cloud_GetBind(cloud, byref(bind), byref(error_code))

    return {'ret': result, 'bind': bind.value, 'code': error_code.value}


def sp_cloud_get_bind_time(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密的换绑周期 (每次调用联网) */
    :param cloud:
    :return: bool, 绑定周期
    """
    sp.SP_Cloud_GetBindTime.argtypes = [c_void_p, POINTER(c_ulonglong), POINTER(c_int)]
    sp.SP_Cloud_GetBindTime.restype = c_bool
    bind_time = c_ulonglong()
    error_code = c_int()
    result = sp.SP_Cloud_GetBindTime(cloud, byref(bind_time), byref(error_code))

    return {'ret': result, 'bind_time': bind_time.value, 'code': error_code.value}


def sp_cloud_get_unbind_deduct_time(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密的解绑扣除属性值 (每次调用联网) */
    :param cloud:
    :return: bool, 解绑扣除属性
    """
    sp.SP_Cloud_GetUnBindDeductTime.argtypes = [c_void_p, POINTER(c_ulonglong), POINTER(c_int)]
    sp.SP_Cloud_GetUnBindDeductTime.restype = c_bool
    deduct_sec = c_ulonglong()
    error_code = c_int()
    result = sp.SP_Cloud_GetUnBindDeductTime(cloud, byref(deduct_sec), byref(error_code))

    return {'ret': result, 'deduct_sec': deduct_sec.value, 'code': error_code.value}


def sp_cloud_get_unbind_max_num(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密的最多解绑次数属性值 (每次调用联网) */
    :param cloud:
    :return: bool, 最多解绑次数
    """
    sp.SP_Cloud_GetUnBindMaxNum.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
    sp.SP_Cloud_GetUnBindMaxNum.restype = c_bool
    num = c_int()
    error_code = c_int()
    result = sp.SP_Cloud_GetUnBindMaxNum(cloud, byref(num), byref(error_code))

    return {'ret': result, 'num': num.value, 'code': error_code.value}


def sp_cloud_get_unbind_count_total(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密的累计解绑次数 (每次调用联网) */
    :param cloud:
    :return: bool, 累计解绑次数
    """
    sp.SP_Cloud_GetUnBindCountTotal.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
    sp.SP_Cloud_GetUnBindCountTotal.restype = c_bool
    count_total = c_int()
    error_code = c_int()
    result = sp.SP_Cloud_GetUnBindCountTotal(cloud, byref(count_total), byref(error_code))

    return {'ret': result, 'count_total': count_total.value, 'code': error_code.value}


def sp_cloud_get_unbind_deduct_time_total(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密的累计解绑扣除的时间 (每次调用联网) */
    :param cloud:
    :return: bool, 累计解绑扣除的时间
    """
    sp.SP_Cloud_GetUnBindDeductTimeTotal.argtypes = [c_void_p, POINTER(c_ulonglong), POINTER(c_int)]
    sp.SP_Cloud_GetUnBindDeductTimeTotal.restype = c_bool
    deduct_time_total = c_ulonglong()
    error_code = c_int()
    result = sp.SP_Cloud_GetUnBindDeductTimeTotal(cloud, byref(deduct_time_total), byref(error_code))

    return {'ret': result, 'deduct_time_total': deduct_time_total.value, 'code': error_code.value}


def sp_cloud_offline(cloud):
    """
    /* 描述: 云计算, 移除当前云计算身份认证信息 (每次调用联网) */
    :param cloud:
    :return: bool
    """
    sp.SP_Cloud_Offline.argtypes = [c_void_p, POINTER(c_int)]
    sp.SP_Cloud_Offline.restype = c_bool
    error_code = c_int()
    result = sp.SP_Cloud_Offline(cloud, byref(error_code))

    return {'ret': result, 'code': error_code.value}


def sp_cloud_get_notices(cloud):
    """
    /* 描述: 通用; 获取公告内容 (每次调用联网) */
    :param cloud:
    :return: bool, 公告内容
    """
    notices = ctypes.create_string_buffer(65535)
    sp.SP_Cloud_GetNotices.argtypes = [c_void_p, POINTER(ctypes.c_char)]
    sp.SP_Cloud_GetNotices.restype = c_bool
    error_code = c_int()
    result = sp.SP_Cloud_GetNotices(cloud, notices, byref(error_code))

    return {'ret': result, 'notices': notices.value.decode('gbk'), 'code': error_code.value}


def sp_cloud_get_card(cloud):
    """
    /* 描述: 云计算, 获取当前登陆的卡密 (不联网; SP_CloudInit 初始化成功后可用) */
    :param cloud:
    :return: bool, 卡密
    """
    sp.SP_Cloud_GetCard.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
    sp.SP_Cloud_GetCard.restype = c_bool
    card = create_string_buffer(42)
    error_code = c_int()
    result = sp.SP_Cloud_GetCard(cloud, card, byref(error_code))

    return {'ret': result, 'card': card.value.decode('gbk'), 'code': error_code.value}


def sp_cloud_get_user(cloud):
    """
    /* 描述: 云计算, 获取当前登陆的账号 (不联网; SP_CloudInit 初始化成功后可用) */
    :param cloud:
    :return: bool, 账号
    """
    sp.SP_Cloud_GetUser.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
    sp.SP_Cloud_GetUser.restype = c_bool
    user = create_string_buffer(33)
    error_code = c_int()
    result = sp.SP_Cloud_GetUser(cloud, user, byref(error_code))

    return {'ret': result, 'user': user.value.decode('gbk'), 'code': error_code.value}


def sp_cloud_disable_card(cloud):
    """
    /* 描述: 云计算, 禁用当前登陆的卡密 (每次调用联网; SP_CloudInit 初始化成功后可用) */
    :param cloud:
    :return:
    """
    sp.SP_Cloud_DisableCard.argtypes = [c_void_p, POINTER(c_int)]
    sp.SP_Cloud_DisableCard.restype = None
    error_code = c_int()
    sp.SP_Cloud_DisableCard(cloud, byref(error_code))

    return {'code': error_code.value}


def sp_cloud_get_cid(cloud):
    """
    /* 描述: 云计算, 获取当前客户端ID (不联网; SP_CloudInit 初始化成功后可用) */
    :param cloud:
    :return: bool, 客户端ID
    """
    sp.SP_Cloud_GetCID.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
    sp.SP_Cloud_GetCID.restype = c_bool
    cid = c_int()
    error_code = c_int()
    result = sp.SP_Cloud_GetCID(cloud, byref(cid), byref(error_code))

    return {'ret': result, 'cid': cid.value, 'code': error_code.value}


def sp_cloud_get_online_count(cloud):
    """
    /* 描述: 云计算, 获取当前卡密在线客户端数量 (SP_CloudInit 初始化成功后可用; 每次调用联网) */
    :param cloud:
    :return: bool, 在线客户端数量
    """
    sp.SP_Cloud_GetOnlineCount.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
    sp.SP_Cloud_GetOnlineCount.restype = c_bool
    count = c_int()
    error_code = c_int()
    result = sp.SP_Cloud_GetOnlineCount(cloud, byref(count), byref(error_code))

    return {'ret': result, 'count': count.value, 'code': error_code.value}


def sp_cloud_set_win_ver(cloud, win_ver):
    """
    /* 描述: 云计算, 设置云计算操作系统版本标识 (不联网; SP_CloudInit 初始化之前使用) */
    :param cloud:
    :param win_ver: windows信息
    :return: bool
    """
    sp.SP_Cloud_SetWinVer.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
    sp.SP_Cloud_SetWinVer.restype = c_bool
    error_code = c_int()
    win_ver = bytes(win_ver, 'gbk')
    result = sp.SP_Cloud_SetWinVer(cloud, win_ver, byref(error_code))

    return {'ret': result, 'code': error_code.value}


def sp_cloud_get_pc_sign(cloud):
    """
    /* 描述: 云计算, 获取网络验证登录时使用的机器码 (不联网); 注意!!! 本接口仅在使用SP_CloudInit且编译生成的软件经过SP加密后生效!!! */
    :param cloud:
    :return: bool, 机器码
    """
    sp.SP_Cloud_GetPCSign.argtypes = [c_void_p, c_char_p]
    sp.SP_Cloud_GetPCSign.restype = c_bool
    pc_sign = create_string_buffer(33)
    result = sp.SP_Cloud_GetPCSign(cloud, pc_sign)

    return {'ret': result, 'pc_sign': pc_sign.value.decode('gbk')}


def sp_cloud_get_unbind_count(cloud):
    """
    /* 描述: 云计算, 获取当前登陆卡密周期内的解绑次数 (每次调用联网) */
    :param cloud:
    :return: bool, 解绑次数
    """
    sp.SP_Cloud_GetUnBindCount.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
    sp.SP_Cloud_GetUnBindCount.restype = c_bool
    count = c_int()
    error_code = c_int()
    result = sp.SP_Cloud_GetUnBindCount(cloud, byref(count), byref(error_code))

    return {'ret': result, 'count': count.value, 'code': error_code.value}


def sp_cloud_get_update_info(cloud):
    """
    /* 描述: 云计算, 获取服务端版本配置信息 (每次调用联网) */
    :param cloud:
    :return: bool, 更新信息, 错误码
    """
    sp.SP_Cloud_GetUpdateInfo.argtypes = [
        c_void_p,
        POINTER(c_int), POINTER(c_int), POINTER(c_int),
        c_char_p, c_char_p, c_char_p,
        POINTER(c_int)
    ]
    sp.SP_Cloud_GetUpdateInfo.restype = c_bool

    b_force = c_int()
    dw_ver = c_int()
    b_direct_url = c_int()
    url = create_string_buffer(2049)
    run_exe = create_string_buffer(101)
    run_cmd = create_string_buffer(129)
    error_code = c_int()

    result = sp.SP_Cloud_GetUpdateInfo(
        cloud,
        byref(b_force), byref(dw_ver), byref(b_direct_url),
        url, run_exe, run_cmd,
        byref(error_code)
    )

    return {
        'ret': result,
        'b_force': b_force.value,
        'dw_ver': dw_ver.value,
        'b_direct_url': b_direct_url.value,
        'url': url.value.decode('gbk'),
        'run_exe': run_exe.value.decode('gbk'),
        'run_cmd': run_cmd.value.decode('gbk'),
        'code': error_code.value
    }


def sp_cloud_get_local_ver_number(cloud):
    """
    /* 描述: 云计算, 获取本地版本号 (不联网; 加密后, SP_CloudInit 初始化成功后可用) */
    :param cloud:
    :return: bool, 本地版本号
    """
    sp.SP_Cloud_GetLocalVerNumber.argtypes = [c_void_p]
    sp.SP_Cloud_GetLocalVerNumber.restype = c_int
    result = sp.SP_Cloud_GetLocalVerNumber(cloud)

    return {'ret': result}


def sp_cloud_get_online_total_count(cloud):
    """
    /* 描述: 云计算, 获取频率验证总在线数量 (每次调用联网; 该功能需要在服务端 [独立软件管理] 开启) */
    :param cloud:
    :return: bool, 在线总数
    """
    sp.SP_Cloud_GetOnlineTotalCount.argtypes = [c_void_p, POINTER(c_uint), POINTER(c_int)]
    sp.SP_Cloud_GetOnlineTotalCount.restype = c_bool
    total_count = c_uint()
    error_code = c_int()
    result = sp.SP_Cloud_GetOnlineTotalCount(cloud, byref(total_count), byref(error_code))

    return {'ret': result, 'total_count': total_count.value, 'code': error_code.value}


def sp_cloud_get_online_cards_count(cloud):
    """
    /* 描述: 云计算, 获取在线卡密数量 (每次调用联网; 该功能需要在服务端 [独立软件管理] 开启) */
    :param cloud:
    :return: bool, 在线卡密数量
    """
    sp.SP_Cloud_GetOnlineCardsCount.argtypes = [c_void_p, POINTER(c_uint), POINTER(c_int)]
    sp.SP_Cloud_GetOnlineCardsCount.restype = c_bool
    total_count = c_uint()
    error_code = c_int()
    result = sp.SP_Cloud_GetOnlineCardsCount(cloud, byref(total_count), byref(error_code))

    return {'ret': result, 'total_count': total_count.value, 'code': error_code.value}


def sp_cloud_get_online_count_by_card(cloud, card):
    """
    /* 描述: 云计算, 获取指定卡密在线链接数量 (每次调用联网) */
    :param cloud:
    :param card: 卡密
    :return: bool, 在线链接数量
    """
    sp.SP_Cloud_GetOnlineCountByCard.argtypes = [c_void_p, c_char_p, POINTER(c_uint), POINTER(c_int)]
    sp.SP_Cloud_GetOnlineCountByCard.restype = c_bool
    total_count = c_uint()
    error_code = c_int()
    card = bytes(card, 'gbk')
    result = sp.SP_Cloud_GetOnlineCountByCard(cloud, card, byref(total_count), byref(error_code))

    return {'ret': result, 'total_count': total_count.value, 'code': error_code.value}


def sp_cloud_query_pc_sign(cloud, card):
    """
    /* 描述: 云计算, 获取指定卡密机器码绑定信息 (每次调用联网) */
    :param cloud:
    :param card: 卡密
    :return: bool, 机器码绑定信息
    """
    sp.SP_Cloud_QueryPCSign.argtypes = [c_void_p, c_char_p, POINTER(POINTER(TagPCSignInfoHead)), POINTER(c_int)]
    sp.SP_Cloud_QueryPCSign.restype = c_bool
    pInfoHead = POINTER(TagPCSignInfoHead)()
    error_code = c_int()
    card = bytes(card, 'gbk')
    result = sp.SP_Cloud_QueryPCSign(cloud, card, byref(pInfoHead), byref(error_code))

    if not result:
        return {'ret': result, 'code': error_code.value}

    info_head = pInfoHead.contents

    ret_data = {
        'u32Count': info_head.u32Count,
        'u32BindIP': info_head.u32BindIP,
        'u32RestCount': info_head.u32RestCount,
        'u64RefreshCountdownSeconds': info_head.u64RefreshCountdownSeconds,
        'u32Limit': info_head.u32Limit,
        'Reserved': [info_head.Reserved[j] for j in range(len(info_head.Reserved))],
        'info': []
    }

    if info_head.u32Count == 0:
        return {'ret': result, 'code': error_code.value, 'info': 'count is 0'}

    if info_head.Info is None:
        return {'ret': result, 'code': error_code.value, 'info': 'NULL'}

    info_data_list = []

    for i in range(info_head.u32Count):
        pc_sign_info = info_head.Info[i]
        info_data_list.append({
                'u64BindTS': pc_sign_info.u64BindTS,
                'szWinVer': pc_sign_info.szWinVer.decode('gbk'),
                'szRemark': pc_sign_info.szRemark.decode('gbk'),
                'szComputerName': pc_sign_info.szComputerName.decode('gbk'),
                'szPCSign': pc_sign_info.szPCSign.decode('gbk'),
                'u64LastLoginTS': pc_sign_info.u64LastLoginTS,
                'Reserved': [pc_sign_info.Reserved[j] for j in range(len(pc_sign_info.Reserved))]
            })
    ret_data['info'] = info_data_list
    return {'ret': result, 'info': ret_data, 'code': error_code.value}


def sp_cloud_user_query_pc_sign(cloud, user, password):
    """
    /* 描述: 云计算, 获取指定用户机器码绑定信息 (每次调用联网) */
    :param cloud:
    :param user: 用户
    :param password: 密码
    :return: bool, 机器码绑定信息
    """
    sp.SP_Cloud_UserQueryPCSign.argtypes = [c_void_p, c_char_p, c_char_p, POINTER(POINTER(TagPCSignInfoHead)), POINTER(c_int)]
    sp.SP_Cloud_UserQueryPCSign.restype = c_bool
    pInfoHead = POINTER(TagPCSignInfoHead)()
    error_code = c_int()
    user = bytes(user, 'gbk')
    password = bytes(password, 'gbk')
    result = sp.SP_Cloud_UserQueryPCSign(cloud, user, password, byref(pInfoHead), byref(error_code))

    if not result:
        return {'ret': result, 'code': error_code.value}

    info_head = pInfoHead.contents

    ret_data = {
        'u32Count': info_head.u32Count,
        'u32BindIP': info_head.u32BindIP,
        'u32RestCount': info_head.u32RestCount,
        'u64RefreshCountdownSeconds': info_head.u64RefreshCountdownSeconds,
        'u32Limit': info_head.u32Limit,
        'Reserved': [info_head.Reserved[j] for j in range(len(info_head.Reserved))],
        'info': []
    }

    if info_head.u32Count == 0:
        return {'ret': result, 'code': error_code.value, 'info': 'count is 0'}

    if info_head.Info is None:
        return {'ret': result, 'code': error_code.value, 'info': 'NULL'}

    info_data_list = []

    for i in range(info_head.u32Count):
        pc_sign_info = info_head.Info[i]
        info_data_list.append({
            'u64BindTS': pc_sign_info.u64BindTS,
            'szWinVer': pc_sign_info.szWinVer.decode('gbk'),
            'szRemark': pc_sign_info.szRemark.decode('gbk'),
            'szComputerName': pc_sign_info.szComputerName.decode('gbk'),
            'szPCSign': pc_sign_info.szPCSign.decode('gbk'),
            'u64LastLoginTS': pc_sign_info.u64LastLoginTS,
            'Reserved': [pc_sign_info.Reserved[j] for j in range(len(pc_sign_info.Reserved))]
        })
    ret_data['info'] = info_data_list
    return {'ret': result, 'info': ret_data, 'code': error_code.value}


def sp_cloud_remove_pc_sign(cloud, card, pc_sign, unbind_ip):
    """
    /* 描述: 通用, 解绑 (每次调用联网) */
    :param cloud:
    :param card: 卡密
    :param pc_sign: 机器码
    :param unbind_ip: 解绑IP
    :return: bool
    """
    sp.SP_Cloud_RemovePCSign.argtypes = [c_void_p, c_char_p, c_char_p, c_uint, POINTER(c_int)]
    sp.SP_Cloud_RemovePCSign.restype = c_bool
    error_code = c_int()
    card = bytes(card, 'gbk')
    pc_sign = bytes(pc_sign, 'gbk')
    unbind_ip = c_uint(unbind_ip)
    result = sp.SP_Cloud_RemovePCSign(cloud, card, pc_sign, unbind_ip, byref(error_code))

    return {'ret': result, 'code': error_code.value}


def sp_cloud_user_remove_pc_sign(cloud, user, password, pc_sign, unbind_ip):
    """
    /* 描述: 通用, 解绑 (每次调用联网) */
    :param cloud:
    :param user: 用户
    :param password: 密码
    :param pc_sign: 机器码
    :param unbind_ip: 解绑IP
    :return: bool
    """
    sp.SP_Cloud_UserRemovePCSign.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_uint, POINTER(c_int)]
    sp.SP_Cloud_UserRemovePCSign.restype = c_bool
    user = bytes(user, 'gbk')
    password = bytes(password, 'gbk')
    pc_sign = bytes(pc_sign, 'gbk')
    error_code = c_int()
    result = sp.SP_Cloud_UserRemovePCSign(cloud, user, password, pc_sign, unbind_ip, byref(error_code))

    return {'ret': result, 'code': error_code.value}


def sp_cloud_query_online(cloud, card):
    """
    /* 描述: 通用; 获取在线客户端信息 (每次调用联网)  */
    :param cloud:
    :param card: 卡密
    :return: bool, 在线客户端信息
    """
    sp.SP_Cloud_QueryOnline.argtypes = [c_void_p, c_char_p, POINTER(POINTER(TagOnlineInfoHead)), POINTER(c_int)]
    sp.SP_Cloud_QueryOnline.restype = c_bool

    info = POINTER(TagOnlineInfoHead)()
    error_code = c_int()

    card_bytes = bytes(card, 'gbk')
    result = sp.SP_Cloud_QueryOnline(cloud, card_bytes, byref(info), byref(error_code))

    if not result:
        return {'ret': result, 'code': error_code.value}

    info_head = info.contents

    ret_data = {
        'u32Count': info_head.u32Count,
        'info': [],
        'Reserved': [info_head.Reserved[j] for j in range(len(info_head.Reserved))]
    }

    if info_head.u32Count == 0:
        return {'ret': result, 'code': error_code.value, 'error': 'count is 0', 'info': ret_data}

    if info_head.Info is None:
        return {'ret': result, 'code': error_code.value, 'error': 'NULL', 'info': ret_data}

    online_info_list = []

    for i in range(info_head.u32Count):
        online_info = info_head.Info[i]
        online_info_list.append({
            "u32CID": online_info.u32CID,
            "szComputerName": online_info.szComputerName.decode('utf-8'),
            "szWinVer": online_info.szWinVer.decode('utf-8'),
            "u64CloudInitTS": online_info.u64CloudInitTS,
            "Reserved": [online_info.Reserved[j] for j in range(20)],
        })

    ret_data['info'] = online_info_list

    return {'ret': result, 'info': ret_data, 'code': error_code.value}


def sp_cloud_user_query_online(cloud, user, password):
    """
    /* 描述: 通用; 获取在线客户端信息 (每次调用联网)  */
    :param cloud:
    :param user: 用户
    :param password: 密码
    :return: bool, 在线客户端信息
    """
    sp.SP_Cloud_UserQueryOnline.argtypes = [c_void_p, c_char_p, c_char_p, POINTER(POINTER(TagOnlineInfoHead)), POINTER(c_int)]
    sp.SP_Cloud_UserQueryOnline.restype = c_bool
    info = POINTER(TagOnlineInfoHead)()
    error_code = c_int()
    user = bytes(user, 'gbk')
    password = bytes(password, 'gbk')
    result = sp.SP_Cloud_UserQueryOnline(cloud, user, password, byref(info), byref(error_code))

    if not result:
        return {'ret': result, 'code': error_code.value}

    info_head = info.contents

    ret_data = {
        'u32Count': info_head.u32Count,
        'Reserved': [info_head.Reserved[j] for j in range(len(info_head.Reserved))],
        'info': []
    }

    if info_head.u32Count == 0:
        return {'ret': result, 'code': error_code.value, 'error': 'count is 0', 'info': ret_data}

    if info_head.Info is None:
        return {'ret': result, 'code': error_code.value, 'error': 'NULL', 'info': ret_data}

    online_info_list = []

    for i in range(info_head.u32Count):
        online_info = info_head.Info[i]
        online_info_list.append({
            "u32CID": online_info.u32CID,
            "szComputerName": online_info.szComputerName.decode('utf-8'),
            "szWinVer": online_info.szWinVer.decode('utf-8'),
            "u64CloudInitTS": online_info.u64CloudInitTS,
            "Reserved": [online_info.Reserved[j] for j in range(20)],
        })

    ret_data['info'] = online_info_list

    return {'ret': result, 'info': ret_data, 'code': error_code.value}


def sp_cloud_close_online_by_cid(cloud, card, cid):
    """
    /* 描述: 通用; 踢掉在线用户 */
    :param cloud:
    :param card: 卡密
    :param cid: 客户端ID
    :return: bool
    """
    sp.SP_Cloud_CloseOnlineByCID.argtypes = [c_void_p, c_char_p, c_uint, POINTER(c_int)]
    sp.SP_Cloud_CloseOnlineByCID.restype = c_bool
    card = bytes(card, 'gbk')
    cid = c_uint(cid)
    error_code = c_int()
    result = sp.SP_Cloud_CloseOnlineByCID(cloud, card, cid, byref(error_code))

    return {'ret': result, 'code': error_code.value}


def sp_cloud_user_close_online_by_cid(cloud, user, password, cid):
    """
    /* 描述: 通用; 踢掉在线用户 */
    :param cloud:
    :param user: 用户
    :param password: 密码
    :param cid: 客户端ID
    :return: bool
    """
    sp.SP_Cloud_UserCloseOnlineByCID.argtypes = [c_void_p, c_char_p, c_char_p, c_uint, POINTER(c_int)]
    sp.SP_Cloud_UserCloseOnlineByCID.restype = c_bool
    error_code = c_int()
    user = bytes(user, 'gbk')
    password = bytes(password, 'gbk')
    result = sp.SP_Cloud_UserCloseOnlineByCID(cloud, user, password, cid, byref(error_code))

    return {'ret': result, 'code': error_code.value}


def sp_cloud_apply_trial_card(cloud):
    """
    /* 描述: 通用; 获取试用卡 */
    :param cloud:
    :return: bool, 卡密
    """
    sp.SP_Cloud_ApplyTrialCard.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
    sp.SP_Cloud_ApplyTrialCard.restype = c_bool
    card = create_string_buffer(42)
    error_code = c_int()
    result = sp.SP_Cloud_ApplyTrialCard(cloud, card, byref(error_code))

    return {'ret': result, 'card': card.value.decode('gbk'), 'code': error_code.value}


def sp_cloud_user_register(cloud, user, password, super_pwd, recharge_cards):
    """
    /* 描述: 通用; 账户注册 (每次调用联网) */
    :param cloud:
    :param user: 用户
    :param password: 密码
    :param super_pwd: 超级密码
    :param recharge_cards: 充值卡密
    :return: bool, 错误码
    """
    sp.SP_Cloud_UserRegister.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_char_p, POINTER(c_int)]
    sp.SP_Cloud_UserRegister.restype = c_bool
    error_code = c_int()
    user = bytes(user, 'gbk')
    password = bytes(password, 'gbk')
    super_pwd = bytes(super_pwd, 'gbk')
    recharge_cards = bytes(recharge_cards, 'gbk')
    result = sp.SP_Cloud_UserRegister(cloud, user, password, super_pwd, recharge_cards, byref(error_code))
    return {'ret': result, 'code': error_code.value}


def sp_cloud_user_recharge(cloud, user, recharge_cards):
    """
    /* 描述: 通用; 账户充值2 (每次调用联网) */
    :param cloud:
    :param user: 用户
    :param recharge_cards: 充值卡密
    :return: bool, 错误码
    """
    sp.SP_Cloud_UserRecharge.argtypes = [c_void_p, c_char_p, c_char_p, POINTER(TagUserRechargedInfo), POINTER(c_int)]
    sp.SP_Cloud_UserRecharge.restype = c_bool
    info = TagUserRechargedInfo()
    error_code = c_int()
    user = bytes(user, 'gbk')
    recharge_cards = bytes(recharge_cards, 'gbk')
    result = sp.SP_Cloud_UserRecharge(cloud, user, recharge_cards, byref(info), byref(error_code))

    ret_data = {
        'u64OldExpiredTimeStamp': info.u64OldExpiredTimeStamp,
        'u64NewExpiredTimeStamp': info.u64NewExpiredTimeStamp,
        'u64OldFYI': info.u64OldFYI,
        'u64NewFYI': info.u64NewFYI,
        'u32RechargeCount': info.u32RechargeCount,
        'Reserved': [info.Reserved[j] for j in range(len(info.Reserved))]
    }

    return {'ret': result, 'info': ret_data, 'code': error_code.value}


def sp_cloud_user_change_pwd(cloud, user, super_pwd, new_password):
    """
    /* 描述: 通用; 账户修改密码 (每次调用联网) */
    :param cloud:
    :param user: 用户
    :param super_pwd: 超级密码
    :param new_password: 新密码
    :return: bool, 错误码
    """
    sp.SP_Cloud_UserChangePWD.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, POINTER(c_int)]
    sp.SP_Cloud_UserChangePWD.restype = c_bool
    error_code = c_int()
    user = bytes(user, 'gbk')
    super_pwd = bytes(super_pwd, 'gbk')
    new_password = bytes(new_password, 'gbk')
    result = sp.SP_Cloud_UserChangePWD(cloud, user, super_pwd, new_password, byref(error_code))

    return {'ret': result, 'code': error_code.value}


def sp_cloud_retrieve_password(cloud, card):
    """
    /* 描述: 通用; 找回密码 (每次调用联网) */
    :param cloud:
    :param card: 卡密
    :return: bool, 用户, 密码, 超级密码
    """
    sp.SP_Cloud_RetrievePassword.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_char_p, POINTER(c_int)]
    sp.SP_Cloud_RetrievePassword.restype = c_bool
    user = create_string_buffer(33)
    password = create_string_buffer(33)
    super_pwd = create_string_buffer(33)
    error_code = c_int()
    card = bytes(card, 'gbk')
    result = sp.SP_Cloud_RetrievePassword(cloud, card, user, password, super_pwd, byref(error_code))

    return {'ret': result, 'user': user.value.decode('gbk'), 'password': password.value.decode('gbk'), 'super_pwd': super_pwd.value.decode('gbk'), 'code': error_code.value}


def sp_cloud_get_basic_info(cloud):
    """
    /* 描述: 通用; 获取基本信息 (每次调用联网) */
    :param cloud:
    :return: bool, 基本信息
    """
    sp.SP_Cloud_GetBasicInfo.argtypes = [c_void_p, POINTER(TagBasicInfo), POINTER(c_int)]
    sp.SP_Cloud_GetBasicInfo.restype = c_bool
    basic_info = TagBasicInfo()
    error_code = c_int()
    result = sp.SP_Cloud_GetBasicInfo(cloud, byref(basic_info), byref(error_code))

    return {
        'ret': result,
        'basic_info': {
            '禁止试用': basic_info.ForbidTrial,
            '禁止软件登录': basic_info.ForbidLogin,
            '禁止软件注册': basic_info.ForbidRegister,
            '禁止软件充值': basic_info.ForbidRecharge,
            '禁止客户端云计算使用': basic_info.ForbidCloudGetCountinfo,
            '保留字段': list(basic_info.Reserved)
        },
        'code': error_code.value
    }


def sp_cloud_malloc(size):
    """
    /* 描述：为了兼容多线程使用封装的申请内存函数 */
    :param size:
    :return:
    """
    sp.SP_Cloud_Malloc.argtypes = [c_int]
    sp.SP_Cloud_Malloc.restype = c_void_p
    sp.SP_Cloud_Malloc(size)

    return None


def sp_cloud_free(buff):
    """
    /* 描述：为了兼容多线程使用封装的释放内存函数 */
    :param buff:
    :return:
    """
    sp.SP_Cloud_Free.argtypes = [c_void_p]
    sp.SP_Cloud_Free.restype = None
    sp.SP_Cloud_Free(buff)

    return None

def sp_cloud_get_error_msg(error_code):
    """
    /* 描述: 查询错误码的简略信息; 详细信息参考文件"云计算错误码 详细信息.txt"; (不联网) */
    :param error_code: 错误码
    :return: 错误信息
    """
    sp.SP_Cloud_GetErrorMsg.argtypes = [c_int, c_char_p]
    sp.SP_Cloud_GetErrorMsg.restype = c_bool
    msg = create_string_buffer(255)
    result = sp.SP_Cloud_GetErrorMsg(error_code, msg)
    if result:
        return  msg.value.decode('gbk')
    else:
        return '未知错误'


def sp_cloud_destroy(cloud):
    """
    /* 描述: 云计算, 销毁一个云计算对象 */
    /*       本函数内部有调用SP_Cloud_Offline做离线处理, 但是可能会因为时机问题导致无法离线 */
    /*       简易最好是调用SP_Cloud_Destroy之前先调用SP_Cloud_Offline下线 */
    :param cloud:
    :return: None
    """
    sp.SP_Cloud_Destroy.argtypes = [c_void_p]
    sp.SP_Cloud_Destroy.restype = None
    return sp.SP_Cloud_Destroy(cloud)


if __name__ == '__main__':
    a = sp_cloud_get_error_msg(-15)
    print(a)