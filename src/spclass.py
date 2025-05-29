import ctypes
from ctypes import *
import os

class SPCloud:
    def __init__(self, dll_path):
        self.init_finish = None
        self.sp = ctypes.WinDLL(dll_path)
        self.cloud = None

    #创建一个装饰器，检查是否已经创建了云计算实例
    @staticmethod
    def check_cloud_created(func):
        def wrapper(self, *args, **kwargs):
            if self.cloud is None:
                raise RuntimeError("请先创建一个云计算对象")
            if not self.init_finish:
                raise RuntimeError("请设置连接信息")
            return func(self, *args, **kwargs)
        return wrapper

    class TagPCSignInfo(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ("u64BindTS", ctypes.c_ulonglong),
            ("szWinVer", ctypes.c_char_p),
            ("szRemark", ctypes.c_char_p),
            ("szComputerName", ctypes.c_char_p),
            ("szPCSign", ctypes.c_char_p),
            ("u64LastLoginTS", ctypes.c_ulonglong),
            ("Reserved", ctypes.c_void_p * 20)
        ]

    class TagPCSignInfoHead(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ("u32Count", ctypes.c_uint),
            ("Info", ctypes.POINTER(ctypes.c_void_p)),  # 需根据实际调整
            ("u32BindIP", ctypes.c_uint),
            ("u32RestCount", ctypes.c_uint),
            ("u64RefreshCountdownSeconds", ctypes.c_ulonglong),
            ("u32Limit", ctypes.c_uint),
            ("Reserved", ctypes.c_void_p * 19)
        ]

    class TagOnlineInfo(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ("u32CID", ctypes.c_uint),
            ("szComputerName", ctypes.c_char_p),
            ("szWinVer", ctypes.c_char_p),
            ("u64CloudInitTS", ctypes.c_ulonglong),
            ("Reserved", ctypes.c_void_p * 20)
        ]

    class TagOnlineInfoHead(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ("u32Count", ctypes.c_uint),
            ("Info", ctypes.POINTER(ctypes.c_void_p)),  # 需根据实际调整
            ("Reserved", ctypes.c_void_p * 20)
        ]

    class TagUserRechargedInfo(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ("u64OldExpiredTimeStamp", ctypes.c_ulonglong),
            ("u64NewExpiredTimeStamp", ctypes.c_ulonglong),
            ("u64OldFYI", ctypes.c_ulonglong),
            ("u64NewFYI", ctypes.c_ulonglong),
            ("u32RechargeCount", ctypes.c_uint),
            ("Reserved", ctypes.c_void_p * 80)
        ]

    class TagBasicInfo(ctypes.Structure):
        _fields_ = [
            ("ForbidTrial", ctypes.c_uint),
            ("ForbidLogin", ctypes.c_uint),
            ("ForbidRegister", ctypes.c_uint),
            ("ForbidRecharge", ctypes.c_uint),
            ("ForbidCloudGetCountinfo", ctypes.c_uint),
            ("Reserved", ctypes.c_uint * 15)
        ]

    # 以下为接口方法，全部搬到类里，调用时用 self.sp
    def cloud_create(self):
        self.sp.SP_Cloud_Create.restype = ctypes.c_void_p
        self.cloud = self.sp.SP_Cloud_Create()
        return self.cloud

    @check_cloud_created
    def card_login(self, card: str):
        error_code = ctypes.c_int()
        self.sp.SP_CloudLogin.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
        self.sp.SP_CloudLogin.restype = ctypes.c_bool
        card = bytes(card, 'gbk')
        ret = self.sp.SP_CloudLogin(self.cloud, card, ctypes.byref(error_code))
        return {'ret': ret, 'code': error_code.value}

    @check_cloud_created
    def user_login(self, user: str, password: str):
        error_code = ctypes.c_int()
        self.sp.SP_CloudUserLogin.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
        self.sp.SP_CloudUserLogin.restype = ctypes.c_bool
        user = bytes(user, 'gbk')
        password = bytes(password, 'gbk')
        ret = self.sp.SP_CloudUserLogin(self.cloud, user, password, ctypes.byref(error_code))
        return {'ret': ret, 'code': error_code.value}

    def cloud_set_conninfo(self, software_name: str, ip: str, port: int, timeout: int,
                              localversion: int, pop_out: c_bool):
        """
        /* 描述: SP云计算_设置连接信息; 不可与SP_CloudInit函数一起使用! */
        :param localversion:
        :param software_name: 软件名称
        :param ip: IP地址
        :param port: 端口
        :param timeout: 超时时间
        :param pop_out: 是否弹窗
        :return: bool
        """
        if self.cloud is None:
            raise Exception('请先创建一个云计算对象')
        software_name = bytes(software_name, 'gbk')
        self.sp.SP_CloudSetConnInfo.argtypes = [c_void_p, c_char_p, c_char_p, c_int, c_int, c_int, c_bool]
        ip = bytes(ip, 'gbk')
        self.sp.SP_CloudSetConnInfo(self.cloud, software_name, ip, port, timeout, localversion, pop_out)
        self.init_finish = True
        return None

    @check_cloud_created
    def cloud_computing(self, cloud_id: int, in_buffer, in_length, retry_count=0, retry_interval_ms=0):
        """
        /* 描述: 云计算请求 (每次调用联网) */
        /* 该函数返回true时, pOutBuffer若不为0, 则需要用户自己释放内存 SP_Cloud_Free(pOutBuffer) */
        :param cloud_id: 云计算ID
        :param in_buffer: 云计算数据包指针
        :param in_length: 云计算数据包长度
        :param retry_count: 重试次数
        :param retry_interval_ms: 重试间隔
        :return: bool
        """
        self.sp.SP_CloudComputing.argtypes = [c_void_p, c_int, POINTER(c_uint), c_uint, POINTER(POINTER(c_uint)),
                                         POINTER(c_uint), POINTER(c_int), c_uint, c_uint]
        self.sp.SP_CloudComputing.restype = c_bool
        out_length = c_uint()
        out_buffer = POINTER(c_uint)()
        error_code = c_int()
        ret = self.sp.SP_CloudComputing(self.cloud, cloud_id, in_buffer, in_length, byref(out_buffer), byref(out_length),
                                   byref(error_code), retry_count, retry_interval_ms)
        return {'ret': ret, 'out_buffer': out_buffer, 'out_length': out_length.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_beat(self):
        """
        /* 描述: 云计算, 频率验证 (每次调用联网; 建议创建一条线程来频繁调用, 比如30秒调用一次) */
        :return: bool
        """
        self.sp.SP_Cloud_Beat.argtypes = [c_void_p, POINTER(c_int)]
        self.sp.SP_Cloud_Beat.restype = c_bool
        error_code = c_int()
        ret = self.sp.SP_Cloud_Beat(self.cloud, byref(error_code))
        return {'ret': ret, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_card_agent(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密所属代理名 (每次调用联网) */
        :return: bool, 代理名
        """
        self.sp.SP_Cloud_GetCardAgent.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
        self.sp.SP_Cloud_GetCardAgent.restype = c_bool
        sz_agent = create_string_buffer(44)
        error_code = c_int()
        ret = self.sp.SP_Cloud_GetCardAgent(self.cloud, sz_agent, byref(error_code))
        return {'ret': ret, 'agent': sz_agent.value.decode('gbk'), 'code': error_code.value}

    @check_cloud_created
    def cloud_get_card_type(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密的卡类型 (每次调用联网) */
        :return: bool, 卡密类型
        """
        self.sp.SP_Cloud_GetCardType.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
        self.sp.SP_Cloud_GetCardType.restype = c_bool
        error_code = c_int()
        card_type = create_string_buffer(36)
        ret = self.sp.SP_Cloud_GetCardType(self.cloud, card_type, byref(error_code))
        return {'ret': ret, 'card_type': card_type.value.decode('gbk'), 'code': error_code.value}

    @check_cloud_created
    def cloud_get_ip_address(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密登录时记录的IP地址 (每次调用联网) */
        :return: bool, IP地址
        """
        self.sp.SP_Cloud_GetIPAddress.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
        self.sp.SP_Cloud_GetIPAddress.restype = c_bool
        error_code = c_int()
        ip_address = create_string_buffer(44)
        ret = self.sp.SP_Cloud_GetIPAddress(self.cloud, ip_address, byref(error_code))
        return {'ret': ret, 'ip_address': ip_address.value.decode('gbk'), 'code': error_code.value}

    @check_cloud_created
    def cloud_get_remarks(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密的备注 (每次调用联网) */
        :return: bool, 备注
        """
        self.sp.SP_Cloud_GetRemarks.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
        self.sp.SP_Cloud_GetRemarks.restype = c_bool
        error_code = c_int()
        remarks = create_string_buffer(132)
        ret = self.sp.SP_Cloud_GetRemarks(self.cloud, remarks, byref(error_code))
        return {'ret': ret, 'remarks': remarks.value.decode('gbk'), 'code': error_code.value}

    @check_cloud_created
    def cloud_get_created_time_stamp(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密的创建时间戳 (每次调用联网) */
        :return: bool, 创建时间戳
        """
        self.sp.SP_Cloud_GetCreatedTimeStamp.argtypes = [c_void_p, POINTER(c_longlong), POINTER(c_int)]
        self.sp.SP_Cloud_GetCreatedTimeStamp.restype = c_bool
        created_time_stamp = c_longlong()
        error_code = c_int()
        ret = self.sp.SP_Cloud_GetCreatedTimeStamp(self.cloud, byref(created_time_stamp), byref(error_code))

        return {'ret': ret, 'created_time_stamp': created_time_stamp.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_activated_time_stamp(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密的激活时间戳 (每次调用联网) */
        :return: bool, 激活时间戳
        """
        self.sp.SP_Cloud_GetActivatedTimeStamp.argtypes = [c_void_p, POINTER(c_ulonglong), POINTER(c_int)]
        self.sp.SP_Cloud_GetActivatedTimeStamp.restype = c_bool
        error_code = c_int()
        activated_time_stamp = c_ulonglong()
        ret = self.sp.SP_Cloud_GetActivatedTimeStamp(self.cloud, byref(activated_time_stamp), byref(error_code))
        return {'ret': ret, 'activated_time_stamp': activated_time_stamp.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_expired_time_stamp(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密的过期时间戳 (每次调用联网) */
        :return: bool, 过期时间戳
        """
        self.sp.SP_Cloud_GetExpiredTimeStamp.argtypes = [c_void_p, POINTER(c_ulonglong), POINTER(c_int)]
        self.sp.SP_Cloud_GetExpiredTimeStamp.restype = c_bool
        error_code = c_int()
        expired_time_stamp = c_ulonglong()
        ret = self.sp.SP_Cloud_GetExpiredTimeStamp(self.cloud, byref(expired_time_stamp), byref(error_code))
        return {'ret': ret, 'expired_time_stamp': expired_time_stamp.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_last_login_time_stamp(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密的最后登录时间戳 (每次调用联网) */
        :return: bool, 最后登录时间戳
        """
        self.sp.SP_Cloud_GetLastLoginTimeStamp.argtypes = [c_void_p, POINTER(c_ulonglong), POINTER(c_int)]
        self.sp.SP_Cloud_GetLastLoginTimeStamp.restype = c_bool
        error_code = c_int()
        last_login_time_stamp = c_ulonglong()
        ret = self.sp.SP_Cloud_GetLastLoginTimeStamp(self.cloud, byref(last_login_time_stamp), byref(error_code))
        return {'ret': ret, 'last_login_time_stamp': last_login_time_stamp.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_fyi(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密的剩余点数 (每次调用联网) */
        :return: bool, 剩余点数
        """
        self.sp.SP_Cloud_GetFYI.argtypes = [c_void_p, POINTER(c_longlong), POINTER(c_int)]
        self.sp.SP_Cloud_GetFYI.restype = c_bool
        fyi = c_longlong()
        error_code = c_int()
        ret = self.sp.SP_Cloud_GetFYI(self.cloud, byref(fyi), byref(error_code))

        return {'ret': ret, 'fyi': fyi.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_deduct_fyi(self, fyi_count):
        """
        /* 描述: 扣除当前卡密点数; 用于用户使用了某些特殊功能需要额外扣费的场景 (每次调用联网) */
        :param fyi_count: 扣点数量
        :return: bool
        """
        self.sp.SP_Cloud_DeductFYI.argtypes = [c_void_p, c_ulonglong, POINTER(c_ulonglong), POINTER(c_int)]
        self.sp.SP_Cloud_DeductFYI.restype = c_bool
        error_code = c_int()
        surplus_fyi = c_ulonglong()
        ret = self.sp.SP_Cloud_DeductFYI(self.cloud, fyi_count, byref(surplus_fyi), byref(error_code))
        return {'ret': ret, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_open_max_num(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密的多开数量属性值 (每次调用联网) */
        :return: bool, 多开数量
        """
        self.sp.SP_Cloud_GetOpenMaxNum.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
        self.sp.SP_Cloud_GetOpenMaxNum.restype = c_bool
        num = c_int()
        error_code = c_int()
        ret = self.sp.SP_Cloud_GetOpenMaxNum(self.cloud, byref(num), byref(error_code))

        return {'ret': ret, 'num': num.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_bind(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密的绑定机器属性值 (每次调用联网) */
        :return: bool, 绑定机器属性
        """
        self.sp.SP_Cloud_GetBind.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
        self.sp.SP_Cloud_GetBind.restype = c_bool
        bind = c_int()
        error_code = c_int()
        result = self.sp.SP_Cloud_GetBind(self.cloud, byref(bind), byref(error_code))

        return {'ret': result, 'bind': bind.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_bind_time(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密的换绑周期 (每次调用联网) */
        :return: bool, 绑定周期
        """
        self.sp.SP_Cloud_GetBindTime.argtypes = [c_void_p, POINTER(c_ulonglong), POINTER(c_int)]
        self.sp.SP_Cloud_GetBindTime.restype = c_bool
        bind_time = c_ulonglong()
        error_code = c_int()
        result = self.sp.SP_Cloud_GetBindTime(self.cloud, byref(bind_time), byref(error_code))

        return {'ret': result, 'bind_time': bind_time.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_unbind_deduct_time(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密的解绑扣除属性值 (每次调用联网) */
        :return: bool, 解绑扣除属性
        """
        self.sp.SP_Cloud_GetUnBindDeductTime.argtypes = [c_void_p, POINTER(c_ulonglong), POINTER(c_int)]
        self.sp.SP_Cloud_GetUnBindDeductTime.restype = c_bool
        deduct_sec = c_ulonglong()
        error_code = c_int()
        result = self.sp.SP_Cloud_GetUnBindDeductTime(self.cloud, byref(deduct_sec), byref(error_code))

        return {'ret': result, 'deduct_sec': deduct_sec.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_unbind_max_num(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密的最多解绑次数属性值 (每次调用联网) */
        :return: bool, 最多解绑次数
        """
        self.sp.SP_Cloud_GetUnBindMaxNum.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
        self.sp.SP_Cloud_GetUnBindMaxNum.restype = c_bool
        num = c_int()
        error_code = c_int()
        result = self.sp.SP_Cloud_GetUnBindMaxNum(self.cloud, byref(num), byref(error_code))

        return {'ret': result, 'num': num.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_unbind_count_total(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密的累计解绑次数 (每次调用联网) */
        :return: bool, 累计解绑次数
        """
        self.sp.SP_Cloud_GetUnBindCountTotal.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
        self.sp.SP_Cloud_GetUnBindCountTotal.restype = c_bool
        count_total = c_int()
        error_code = c_int()
        result = self.sp.SP_Cloud_GetUnBindCountTotal(self.cloud, byref(count_total), byref(error_code))

        return {'ret': result, 'count_total': count_total.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_unbind_deduct_time_total(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密的累计解绑扣除的时间 (每次调用联网) */
        :return: bool, 累计解绑扣除的时间
        """
        self.sp.SP_Cloud_GetUnBindDeductTimeTotal.argtypes = [c_void_p, POINTER(c_ulonglong), POINTER(c_int)]
        self.sp.SP_Cloud_GetUnBindDeductTimeTotal.restype = c_bool
        deduct_time_total = c_ulonglong()
        error_code = c_int()
        result = self.sp.SP_Cloud_GetUnBindDeductTimeTotal(self.cloud, byref(deduct_time_total), byref(error_code))

        return {'ret': result, 'deduct_time_total': deduct_time_total.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_offline(self):
        """
        /* 描述: 云计算, 移除当前云计算身份认证信息 (每次调用联网) */
        :return: bool
        """
        self.sp.SP_Cloud_Offline.argtypes = [c_void_p, POINTER(c_int)]
        self.sp.SP_Cloud_Offline.restype = c_bool
        error_code = c_int()
        result = self.sp.SP_Cloud_Offline(self.cloud, byref(error_code))

        return {'ret': result, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_notices(self):
        """
        /* 描述: 通用; 获取公告内容 (每次调用联网) */
        :return: bool, 公告内容
        """
        notices = ctypes.create_string_buffer(65535)
        self.sp.SP_Cloud_GetNotices.argtypes = [c_void_p, POINTER(ctypes.c_char)]
        self.sp.SP_Cloud_GetNotices.restype = c_bool
        error_code = c_int()
        result = self.sp.SP_Cloud_GetNotices(self.cloud, notices)#, byref(error_code))

        return {'ret': result, 'notices': notices.value.decode('gbk'), 'code': error_code.value}

    @check_cloud_created
    def cloud_get_card(self):
        """
        /* 描述: 云计算, 获取当前登陆的卡密 (不联网; SP_CloudInit 初始化成功后可用) */
        :return: bool, 卡密
        """
        self.sp.SP_Cloud_GetCard.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
        self.sp.SP_Cloud_GetCard.restype = c_bool
        card = create_string_buffer(42)
        error_code = c_int()
        result = self.sp.SP_Cloud_GetCard(self.cloud, card, byref(error_code))

        return {'ret': result, 'card': card.value.decode('gbk'), 'code': error_code.value}

    @check_cloud_created
    def cloud_get_user(self):
        """
        /* 描述: 云计算, 获取当前登陆的账号 (不联网; SP_CloudInit 初始化成功后可用) */
        :return: bool, 账号
        """
        self.sp.SP_Cloud_GetUser.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
        self.sp.SP_Cloud_GetUser.restype = c_bool
        user = create_string_buffer(33)
        error_code = c_int()
        result = self.sp.SP_Cloud_GetUser(self.cloud, user, byref(error_code))

        return {'ret': result, 'user': user.value.decode('gbk'), 'code': error_code.value}

    @check_cloud_created
    def cloud_disable_card(self):
        """
        /* 描述: 云计算, 禁用当前登陆的卡密 (每次调用联网; SP_CloudInit 初始化成功后可用) */
        :return:
        """
        self.sp.SP_Cloud_DisableCard.argtypes = [c_void_p, POINTER(c_int)]
        self.sp.SP_Cloud_DisableCard.restype = None
        error_code = c_int()
        self.sp.SP_Cloud_DisableCard(self.cloud, byref(error_code))

        return {'code': error_code.value}

    @check_cloud_created
    def cloud_get_cid(self):
        """
        /* 描述: 云计算, 获取当前客户端ID (不联网; SP_CloudInit 初始化成功后可用) */
        :return: bool, 客户端ID
        """
        self.sp.SP_Cloud_GetCID.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
        self.sp.SP_Cloud_GetCID.restype = c_bool
        cid = c_int()
        error_code = c_int()
        result = self.sp.SP_Cloud_GetCID(self.cloud, byref(cid), byref(error_code))

        return {'ret': result, 'cid': cid.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_online_count(self):
        """
        /* 描述: 云计算, 获取当前卡密在线客户端数量 (SP_CloudInit 初始化成功后可用; 每次调用联网) */
        :return: bool, 在线客户端数量
        """
        self.sp.SP_Cloud_GetOnlineCount.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
        self.sp.SP_Cloud_GetOnlineCount.restype = c_bool
        count = c_int()
        error_code = c_int()
        result = self.sp.SP_Cloud_GetOnlineCount(self.cloud, byref(count), byref(error_code))

        return {'ret': result, 'count': count.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_set_win_ver(self, win_ver):
        """
        /* 描述: 云计算, 设置云计算操作系统版本标识 (不联网; SP_CloudInit 初始化之前使用) */
        :param win_ver: windows信息
        :return: bool
        """
        self.sp.SP_Cloud_SetWinVer.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
        self.sp.SP_Cloud_SetWinVer.restype = c_bool
        error_code = c_int()
        win_ver = bytes(win_ver, 'gbk')
        result = self.sp.SP_Cloud_SetWinVer(self.cloud, win_ver, byref(error_code))

        return {'ret': result, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_pc_sign(self):
        """
        /* 描述: 云计算, 获取网络验证登录时使用的机器码 (不联网); 注意!!! 本接口仅在使用SP_CloudInit且编译生成的软件经过SP加密后生效!!! */
        :return: bool, 机器码
        """
        self.sp.SP_Cloud_GetPCSign.argtypes = [c_void_p, c_char_p]
        self.sp.SP_Cloud_GetPCSign.restype = c_bool
        pc_sign = create_string_buffer(33)
        result = self.sp.SP_Cloud_GetPCSign(self.cloud, pc_sign)

        return {'ret': result, 'pc_sign': pc_sign.value.decode('gbk')}

    @check_cloud_created
    def cloud_get_unbind_count(self):
        """
        /* 描述: 云计算, 获取当前登陆卡密周期内的解绑次数 (每次调用联网) */
        :return: bool, 解绑次数
        """
        self.sp.SP_Cloud_GetUnBindCount.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
        self.sp.SP_Cloud_GetUnBindCount.restype = c_bool
        count = c_int()
        error_code = c_int()
        result = self.sp.SP_Cloud_GetUnBindCount(self.cloud, byref(count), byref(error_code))

        return {'ret': result, 'count': count.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_update_info(self):
        """
        /* 描述: 云计算, 获取服务端版本配置信息 (每次调用联网) */
        :return: bool, 更新信息, 错误码
        """
        self.sp.SP_Cloud_GetUpdateInfo.argtypes = [
            c_void_p,
            POINTER(c_int), POINTER(c_int), POINTER(c_int),
            c_char_p, c_char_p, c_char_p,
            POINTER(c_int)
        ]
        self.sp.SP_Cloud_GetUpdateInfo.restype = c_bool

        b_force = c_int()
        dw_ver = c_int()
        b_direct_url = c_int()
        url = create_string_buffer(2049)
        run_exe = create_string_buffer(101)
        run_cmd = create_string_buffer(129)
        error_code = c_int()

        result = self.sp.SP_Cloud_GetUpdateInfo(
            self.cloud,
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

    @check_cloud_created
    def cloud_get_local_ver_number(self):
        """
        /* 描述: 云计算, 获取本地版本号 (不联网; 加密后, SP_CloudInit 初始化成功后可用) */
        :return: bool, 本地版本号
        """
        self.sp.SP_Cloud_GetLocalVerNumber.argtypes = [c_void_p]
        self.sp.SP_Cloud_GetLocalVerNumber.restype = c_int
        result = self.sp.SP_Cloud_GetLocalVerNumber(self.cloud)

        return {'ret': result}

    @check_cloud_created
    def cloud_get_online_total_count(self):
        """
        /* 描述: 云计算, 获取频率验证总在线数量 (每次调用联网; 该功能需要在服务端 [独立软件管理] 开启) */
        :return: bool, 在线总数
        """
        self.sp.SP_Cloud_GetOnlineTotalCount.argtypes = [c_void_p, POINTER(c_uint), POINTER(c_int)]
        self.sp.SP_Cloud_GetOnlineTotalCount.restype = c_bool
        total_count = c_uint()
        error_code = c_int()
        result = self.sp.SP_Cloud_GetOnlineTotalCount(self.cloud, byref(total_count), byref(error_code))

        return {'ret': result, 'total_count': total_count.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_online_cards_count(self):
        """
        /* 描述: 云计算, 获取在线卡密数量 (每次调用联网; 该功能需要在服务端 [独立软件管理] 开启) */
        :return: bool, 在线卡密数量
        """
        self.sp.SP_Cloud_GetOnlineCardsCount.argtypes = [c_void_p, POINTER(c_uint), POINTER(c_int)]
        self.sp.SP_Cloud_GetOnlineCardsCount.restype = c_bool
        total_count = c_uint()
        error_code = c_int()
        result = self.sp.SP_Cloud_GetOnlineCardsCount(self.cloud, byref(total_count), byref(error_code))

        return {'ret': result, 'total_count': total_count.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_get_online_count_by_card(self, card):
        """
        /* 描述: 云计算, 获取指定卡密在线链接数量 (每次调用联网) */
        :param card: 卡密
        :return: bool, 在线链接数量
        """
        self.sp.SP_Cloud_GetOnlineCountByCard.argtypes = [c_void_p, c_char_p, POINTER(c_uint), POINTER(c_int)]
        self.sp.SP_Cloud_GetOnlineCountByCard.restype = c_bool
        total_count = c_uint()
        error_code = c_int()
        card = bytes(card, 'gbk')
        result = self.sp.SP_Cloud_GetOnlineCountByCard(self.cloud, card, byref(total_count), byref(error_code))

        return {'ret': result, 'total_count': total_count.value, 'code': error_code.value}

    @check_cloud_created
    def cloud_query_pc_sign(self, card):
        """
        /* 描述: 云计算, 获取指定卡密机器码绑定信息 (每次调用联网) */
        :param card: 卡密
        :return: bool, 机器码绑定信息
        """
        self.sp.SP_Cloud_QueryPCSign.argtypes = [c_void_p, c_char_p, POINTER(POINTER(self.TagPCSignInfoHead)), POINTER(c_int)]
        self.sp.SP_Cloud_QueryPCSign.restype = c_bool
        pInfoHead = POINTER(self.TagPCSignInfoHead)()
        error_code = c_int()
        card = bytes(card, 'gbk')
        result = self.sp.SP_Cloud_QueryPCSign(self.cloud, card, byref(pInfoHead), byref(error_code))

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

    @check_cloud_created
    def cloud_user_query_pc_sign(self, user, password):
        """
        /* 描述: 云计算, 获取指定用户机器码绑定信息 (每次调用联网) */
        :param user: 用户
        :param password: 密码
        :return: bool, 机器码绑定信息
        """
        self.sp.SP_Cloud_UserQueryPCSign.argtypes = [c_void_p, c_char_p, c_char_p, POINTER(POINTER(self.TagPCSignInfoHead)),
                                                POINTER(c_int)]
        self.sp.SP_Cloud_UserQueryPCSign.restype = c_bool
        pInfoHead = POINTER(self.TagPCSignInfoHead)()
        error_code = c_int()
        user = bytes(user, 'gbk')
        password = bytes(password, 'gbk')
        result = self.sp.SP_Cloud_UserQueryPCSign(self.cloud, user, password, byref(pInfoHead), byref(error_code))

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

    @check_cloud_created
    def cloud_remove_pc_sign(self, card, pc_sign, unbind_ip):
        """
        /* 描述: 通用, 解绑 (每次调用联网) */
        :param card: 卡密
        :param pc_sign: 机器码
        :param unbind_ip: 解绑IP
        :return: bool
        """
        self.sp.SP_Cloud_RemovePCSign.argtypes = [c_void_p, c_char_p, c_char_p, c_uint, POINTER(c_int)]
        self.sp.SP_Cloud_RemovePCSign.restype = c_bool
        error_code = c_int()
        card = bytes(card, 'gbk')
        pc_sign = bytes(pc_sign, 'gbk')
        unbind_ip = c_uint(unbind_ip)
        result = self.sp.SP_Cloud_RemovePCSign(self.cloud, card, pc_sign, unbind_ip, byref(error_code))

        return {'ret': result, 'code': error_code.value}

    @check_cloud_created
    def cloud_user_remove_pc_sign(self, user, password, pc_sign, unbind_ip):
        """
        /* 描述: 通用, 解绑 (每次调用联网) */
        :param user: 用户
        :param password: 密码
        :param pc_sign: 机器码
        :param unbind_ip: 解绑IP
        :return: bool
        """
        self.sp.SP_Cloud_UserRemovePCSign.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_uint, POINTER(c_int)]
        self.sp.SP_Cloud_UserRemovePCSign.restype = c_bool
        user = bytes(user, 'gbk')
        password = bytes(password, 'gbk')
        pc_sign = bytes(pc_sign, 'gbk')
        error_code = c_int()
        result = self.sp.SP_Cloud_UserRemovePCSign(self.cloud, user, password, pc_sign, unbind_ip, byref(error_code))

        return {'ret': result, 'code': error_code.value}

    @check_cloud_created
    def cloud_query_online(self, card):
        """
        /* 描述: 通用; 获取在线客户端信息 (每次调用联网)  */
        :param card: 卡密
        :return: bool, 在线客户端信息
        """
        self.sp.SP_Cloud_QueryOnline.argtypes = [c_void_p, c_char_p, POINTER(POINTER(self.TagOnlineInfoHead)), POINTER(c_int)]
        self.sp.SP_Cloud_QueryOnline.restype = c_bool

        info = POINTER(self.TagOnlineInfoHead)()
        error_code = c_int()

        card_bytes = bytes(card, 'gbk')
        result = self.sp.SP_Cloud_QueryOnline(self.cloud, card_bytes, byref(info), byref(error_code))

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

    @check_cloud_created
    def cloud_user_query_online(self, user, password):
        """
        /* 描述: 通用; 获取在线客户端信息 (每次调用联网)  */
        :param user: 用户
        :param password: 密码
        :return: bool, 在线客户端信息
        """
        self.sp.SP_Cloud_UserQueryOnline.argtypes = [c_void_p, c_char_p, c_char_p, POINTER(POINTER(self.TagOnlineInfoHead)),
                                                POINTER(c_int)]
        self.sp.SP_Cloud_UserQueryOnline.restype = c_bool
        info = POINTER(self.TagOnlineInfoHead)()
        error_code = c_int()
        user = bytes(user, 'gbk')
        password = bytes(password, 'gbk')
        result = self.sp.SP_Cloud_UserQueryOnline(self.cloud, user, password, byref(info), byref(error_code))

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

    @check_cloud_created
    def cloud_close_online_by_cid(self, card, cid):
        """
        /* 描述: 通用; 踢掉在线用户 */
        :param card: 卡密
        :param cid: 客户端ID
        :return: bool
        """
        self.sp.SP_Cloud_CloseOnlineByCID.argtypes = [c_void_p, c_char_p, c_uint, POINTER(c_int)]
        self.sp.SP_Cloud_CloseOnlineByCID.restype = c_bool
        card = bytes(card, 'gbk')
        cid = c_uint(cid)
        error_code = c_int()
        result = self.sp.SP_Cloud_CloseOnlineByCID(self.cloud, card, cid, byref(error_code))

        return {'ret': result, 'code': error_code.value}

    @check_cloud_created
    def cloud_user_close_online_by_cid(self, user, password, cid):
        """
        /* 描述: 通用; 踢掉在线用户 */
        :param user: 用户
        :param password: 密码
        :param cid: 客户端ID
        :return: bool
        """
        self.sp.SP_Cloud_UserCloseOnlineByCID.argtypes = [c_void_p, c_char_p, c_char_p, c_uint, POINTER(c_int)]
        self.sp.SP_Cloud_UserCloseOnlineByCID.restype = c_bool
        error_code = c_int()
        user = bytes(user, 'gbk')
        password = bytes(password, 'gbk')
        result = self.sp.SP_Cloud_UserCloseOnlineByCID(self.cloud, user, password, cid, byref(error_code))

        return {'ret': result, 'code': error_code.value}

    @check_cloud_created
    def cloud_apply_trial_card(self):
        """
        /* 描述: 通用; 获取试用卡 */
        :return: bool, 卡密
        """
        self.sp.SP_Cloud_ApplyTrialCard.argtypes = [c_void_p, c_char_p, POINTER(c_int)]
        self.sp.SP_Cloud_ApplyTrialCard.restype = c_bool
        card = create_string_buffer(42)
        error_code = c_int()
        result = self.sp.SP_Cloud_ApplyTrialCard(self.cloud, card, byref(error_code))

        return {'ret': result, 'card': card.value.decode('gbk'), 'code': error_code.value}

    @check_cloud_created
    def cloud_user_register(self, user, password, super_pwd, recharge_cards):
        """
        /* 描述: 通用; 账户注册 (每次调用联网) */
        :param user: 用户
        :param password: 密码
        :param super_pwd: 超级密码
        :param recharge_cards: 充值卡密
        :return: bool, 错误码
        """
        self.sp.SP_Cloud_UserRegister.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_char_p, POINTER(c_int)]
        self.sp.SP_Cloud_UserRegister.restype = c_bool
        error_code = c_int()
        user = bytes(user, 'gbk')
        password = bytes(password, 'gbk')
        super_pwd = bytes(super_pwd, 'gbk')
        recharge_cards = bytes(recharge_cards, 'gbk')
        result = self.sp.SP_Cloud_UserRegister(self.cloud, user, password, super_pwd, recharge_cards, byref(error_code))
        return {'ret': result, 'code': error_code.value}

    @check_cloud_created
    def cloud_user_recharge(self, user, recharge_cards):
        """
        /* 描述: 通用; 账户充值2 (每次调用联网) */
        :param user: 用户
        :param recharge_cards: 充值卡密
        :return: bool, 错误码
        """
        self.sp.SP_Cloud_UserRecharge.argtypes = [c_void_p, c_char_p, c_char_p, POINTER(self.TagUserRechargedInfo),
                                             POINTER(c_int)]
        self.sp.SP_Cloud_UserRecharge.restype = c_bool
        info = self.TagUserRechargedInfo()
        error_code = c_int()
        user = bytes(user, 'gbk')
        recharge_cards = bytes(recharge_cards, 'gbk')
        result = self.sp.SP_Cloud_UserRecharge(self.cloud, user, recharge_cards, byref(info), byref(error_code))

        ret_data = {
            'u64OldExpiredTimeStamp': info.u64OldExpiredTimeStamp,
            'u64NewExpiredTimeStamp': info.u64NewExpiredTimeStamp,
            'u64OldFYI': info.u64OldFYI,
            'u64NewFYI': info.u64NewFYI,
            'u32RechargeCount': info.u32RechargeCount,
            'Reserved': [info.Reserved[j] for j in range(len(info.Reserved))]
        }

        return {'ret': result, 'info': ret_data, 'code': error_code.value}

    @check_cloud_created
    def cloud_user_change_pwd(self, user, super_pwd, new_password):
        """
        /* 描述: 通用; 账户修改密码 (每次调用联网) */
        :param user: 用户
        :param super_pwd: 超级密码
        :param new_password: 新密码
        :return: bool, 错误码
        """
        self.sp.SP_Cloud_UserChangePWD.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, POINTER(c_int)]
        self.sp.SP_Cloud_UserChangePWD.restype = c_bool
        error_code = c_int()
        user = bytes(user, 'gbk')
        super_pwd = bytes(super_pwd, 'gbk')
        new_password = bytes(new_password, 'gbk')
        result = self.sp.SP_Cloud_UserChangePWD(self.cloud, user, super_pwd, new_password, byref(error_code))

        return {'ret': result, 'code': error_code.value}

    @check_cloud_created
    def cloud_retrieve_password(self, card):
        """
        /* 描述: 通用; 找回密码 (每次调用联网) */
        :param card: 卡密
        :return: bool, 用户, 密码, 超级密码
        """
        self.sp.SP_Cloud_RetrievePassword.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_char_p, POINTER(c_int)]
        self.sp.SP_Cloud_RetrievePassword.restype = c_bool
        user = create_string_buffer(33)
        password = create_string_buffer(33)
        super_pwd = create_string_buffer(33)
        error_code = c_int()
        card = bytes(card, 'gbk')
        result = self.sp.SP_Cloud_RetrievePassword(self.cloud, card, user, password, super_pwd, byref(error_code))

        return {'ret': result, 'user': user.value.decode('gbk'), 'password': password.value.decode('gbk'),
                'super_pwd': super_pwd.value.decode('gbk'), 'code': error_code.value}

    @check_cloud_created
    def cloud_get_basic_info(self):
        """
        /* 描述: 通用; 获取基本信息 (每次调用联网) */
        :return: bool, 基本信息
        """
        self.sp.SP_Cloud_GetBasicInfo.argtypes = [c_void_p, POINTER(self.TagBasicInfo), POINTER(c_int)]
        self.sp.SP_Cloud_GetBasicInfo.restype = c_bool
        basic_info = self.TagBasicInfo()
        error_code = c_int()
        result = self.sp.SP_Cloud_GetBasicInfo(self.cloud, byref(basic_info), byref(error_code))

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

    def cloud_malloc(self, size):
        """
        /* 描述：为了兼容多线程使用封装的申请内存函数 */
        :param size:
        :return:
        """
        self.sp.SP_Cloud_Malloc.argtypes = [c_int]
        self.sp.SP_Cloud_Malloc.restype = c_void_p
        self.sp.SP_Cloud_Malloc(size)

        return None

    def cloud_free(self, buff):
        """
        /* 描述：为了兼容多线程使用封装的释放内存函数 */
        :param buff:
        :return:
        """
        self.sp.SP_Cloud_Free.argtypes = [c_void_p]
        self.sp.SP_Cloud_Free.restype = None
        self.sp.SP_Cloud_Free(buff)

        return None

    def cloud_get_error_msg(self, error_code):
        """
        /* 描述: 查询错误码的简略信息; 详细信息参考文件"云计算错误码 详细信息.txt"; (不联网) */
        :param error_code: 错误码
        :return: 错误信息
        """
        self.sp.SP_Cloud_GetErrorMsg.argtypes = [c_int, c_char_p]
        self.sp.SP_Cloud_GetErrorMsg.restype = c_bool
        msg = create_string_buffer(255)
        result = self.sp.SP_Cloud_GetErrorMsg(error_code, msg)
        if result:
            return msg.value.decode('gbk')
        else:
            return '未知错误'

    @check_cloud_created
    def cloud_destroy(self):
        """
        /* 描述: 云计算, 销毁一个云计算对象 */
        /*       本函数内部有调用SP_Cloud_Offline做离线处理, 但是可能会因为时机问题导致无法离线 */
        /*       简易最好是调用SP_Cloud_Destroy之前先调用SP_Cloud_Offline下线 */
        :return: None
        """
        self.sp.SP_Cloud_Destroy.argtypes = [c_void_p]
        self.sp.SP_Cloud_Destroy.restype = None
        return self.sp.SP_Cloud_Destroy(self.cloud)


if __name__ == '__main__':
    # pass
    import time
    cloud = SPCloud('..\SPCloud64_Py.dll')
    #
    cloud.cloud_create()
    cloud.cloud_set_conninfo('','' , 8896, 300, 1, c_bool(False))
    # ret = cloud.card_login('')
    # beat = cloud.cloud_beat()
    # print(beat)
    # t1 = time.time()
    # agent = cloud.cloud_get_card_agent()
    # print(agent)
    # t2 = time.time()
    # print(t2 - t1)
    # card_type = cloud.cloud_get_card_type()
    # print(card_type)

    # login_ip = cloud.cloud_get_ip_address()
    # print(login_ip)
    #
    # remarks = cloud.cloud_get_remarks()
    # print(remarks)
    #
    # create_time_stamp = cloud.cloud_get_created_time_stamp()
    # print(create_time_stamp)
    #
    # activated_time_stamp = cloud.cloud_get_activated_time_stamp()
    # print(activated_time_stamp)
    #
    # expired_time_stamp = cloud.cloud_get_expired_time_stamp()
    # print(expired_time_stamp)
    #
    # old_point = cloud.cloud_get_fyi()
    # print(old_point)
    #
    # deduct_fyi = cloud.cloud_deduct_fyi(1)
    # print(deduct_fyi)
    #
    # new_point = cloud.cloud_get_fyi()
    # print(new_point)
    #
    # open_max_num = cloud.cloud_get_open_max_num()
    # print(open_max_num)
    #
    # bind = cloud.cloud_get_bind()
    # print(bind)
    #
    # bind_time = cloud.cloud_get_bind_time()
    # print(bind_time)
    #
    # unbind_deduct_time = cloud.cloud_get_unbind_deduct_time()
    # print(unbind_deduct_time)
    #
    # unbind_max_num = cloud.cloud_get_unbind_max_num()
    # print(unbind_max_num)
    #
    # unbind_count_total = cloud.cloud_get_unbind_count_total()
    # print(unbind_count_total)
    #
    # unbind_deduct_time_total = cloud.cloud_get_unbind_deduct_time_total()
    # print(unbind_deduct_time_total)

    notice = cloud.cloud_get_notices()
    print(notice)

    # cards = cloud.cloud_get_card()
    # print(cards)
    #
    # CID = cloud.cloud_get_cid()
    # print(CID)
    #
    # online_count = cloud.cloud_get_online_count()
    # print(online_count)
    #
    # # win_ver = cloud.cloud_set_win_ver()
    # # print(win_ver)
    #
    # pc_sign = cloud.cloud_get_pc_sign()
    # print(pc_sign)
    #
    # unbind_count = cloud.cloud_get_unbind_count()
    # print(unbind_count)
    #
    # update_info = cloud.cloud_get_update_info()
    # print(update_info)
    #
    # # local_ver_number = cloud.cloud_get_local_ver_number()
    # # print(local_ver_number)
    #
    # online_total_count = cloud.cloud_get_online_total_count()
    # print(online_total_count)
    #
    # online_cards_count = cloud.cloud_get_online_cards_count()
    # print(online_cards_count)
    #
    # online_count_by_card = cloud.cloud_get_online_count_by_card('')
    # print(online_count_by_card)
    #
    # target_pc_sign = cloud.cloud_query_pc_sign('')
    # print(target_pc_sign)
    #
    # remove_pc_sign = cloud.cloud_remove_pc_sign('', pc_sign['pc_sign'], 1)
    # print(remove_pc_sign)
    #
    # query_online = cloud.cloud_query_online('')
    # print(query_online)
    #
    # close_online_by_cid = cloud.cloud_close_online_by_cid('', CID['cid'])
    # print(close_online_by_cid)
    #
    # trail_card = cloud.cloud_apply_trial_card()
    # print(trail_card)
    #
    # basic_info = cloud.cloud_get_basic_info()
    # print(basic_info)
    #
    # # 禁用卡密
    # # disable_card = cloud.cloud_disable_card()
    # # print(disable_card)
    #
    # cloud.cloud_offline()
    # cloud.cloud_destroy()
    # print('finished')