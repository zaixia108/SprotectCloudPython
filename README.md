## 快速开始

### 1. 初始化云计算对象

```python
from sp.sp import SPCloud
from ctypes import c_bool

cloud = SPCloud(SP的dll目录)
cloud.cloud_create()
```

### 2. 设置连接信息

```python
cloud.cloud_set_conninfo(
    software_name='YourSoftwareName',
    ip='服务器IP或域名',
    port=端口号,                 # 例如 8896
    timeout=超时时间秒,           # 例如 300
    localversion=本地版本号,       # 例如 1
    pop_out=c_bool(False)        # 是否弹窗
)
```

### 3. 卡密登录 或 账号登录

**卡密登录：**
```python
login_result = cloud.card_login('你的卡密')
print(login_result)  # {'ret': True/False, 'code': 错误码}
```

**账号登录：**
```python
login_result = cloud.user_login('账号', '密码')
print(login_result)
```

### 4. 常用接口举例

#### 获取卡密代理名
```python
agent = cloud.cloud_get_card_agent()
print(agent)
```

#### 获取卡密类型
```python
card_type = cloud.cloud_get_card_type()
print(card_type)
```

#### 获取卡密IP地址
```python
ip_info = cloud.cloud_get_ip_address()
print(ip_info)
```

#### 获取公告内容
```python
notices = cloud.cloud_get_notices()
print(notices)
```

#### 获取点数
```python
fyi = cloud.cloud_get_fyi()
print(fyi)
```

#### 扣除点数
```python
deduct_result = cloud.cloud_deduct_fyi(点数数量)
print(deduct_result)
```

### 5. 下线与销毁对象

```python
cloud.cloud_offline()
cloud.cloud_destroy()
```

## 其他接口说明

`SPCloud` 封装了大部分云计算常用接口，包括：

- 用户注册、充值、改密码
- 查询/解绑机器码
- 查询在线信息、踢用户下线
- 获取/申请试用卡
- 获取/禁用当前卡密
- 获取/设置本地版本号、客户端ID等
- 错误码查询（`cloud_get_error_msg`）

每个方法均有 docstring，参数类型、返回值及异常说明可参见源码。

## 错误处理

所有调用如未登录、未初始化等，均会抛出异常或返回 `{'ret': False, 'code': 错误码}` 格式。可通过 `cloud.cloud_get_error_msg(错误码)` 获取详细错误信息。

## 示例代码

见 `sp/spclass.py` 文件末尾的 `if __name__ == '__main__':` 区块，包含了完整的调用演示。

## 常见问题

- **Q1:** DLL 加载失败？
  - 请确保 `SPCloud64_Py.dll`和`SProtectSDK64.dll` 目录正确，且操作系统为 Windows。
- **Q2:** 字符串参数乱码？
  - 所有字符串参数均按 `gbk` 编码传递，返回值解码同样如此。

## 许可证

本仓库仅供学习和内部集成测试使用。如需商业或大规模场景使用，请联系原作者或官方获取授权。

---
如有疑问或 bug，欢迎提 issue 或联系作者。