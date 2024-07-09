import json
import hashlib
import os
import re
import time
import asyncio
import aiohttp
import uuid
from rich import print_json

DEBUG_MODE = False  # Debug模式，是否打印请求返回信息
PROXY = ''  # 代理，如果多次出现IP问题可尝试将自己所用的代理，例如使用clash则设置为 'http://127.0.0.1:7890'
PUSHPLUS_TOKEN = os.getenv('PUSHPLUS_TOKEN') or ''
INVITE_CODE = os.getenv('INVITE_CODE') or input('请输入邀请码: ')
PUSH_MSG = ''

# 检查变量
def check_env():
    invite_code_list = []
    if not PUSHPLUS_TOKEN:
        print('请按照文档设置PUSHPLUS_TOKEN环境变量')
    if not INVITE_CODE:
        print('请按照文档设置INVITE_CODE环境变量')
        raise Exception('请按照文档设置INVITE_CODE环境变量')
    else:
        if '@' in INVITE_CODE:
            invite_code_list = INVITE_CODE.split('@')
        elif '\n' in INVITE_CODE:
            invite_code_list = INVITE_CODE.split('\n')
        else:
            invite_code_list.append(INVITE_CODE)
        return invite_code_list

# 推送
async def push(content):
    if PUSHPLUS_TOKEN:
        url = 'http://www.pushplus.plus/send'
        data = {
            "token": PUSHPLUS_TOKEN,
            "title": 'PikPak邀请通知',
            "content": content,
        }
        headers = {'Content-Type': 'application/json'}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=json.dumps(data)) as response:
                    response_data = await response.json()
                    if response_data['code'] == 200:
                        print('推送成功')
                    else:
                        print(f'推送失败，{response_data["msg"]}')
        except Exception as e:
            print(e)

# 滑块数据加密
def r(e, t):
    n = t - 1
    if n < 0:
        n = 0
    r = e[n]
    u = r["row"] // 2 + 1
    c = r["column"] // 2 + 1
    f = r["matrix"][u][c]
    l = t + 1
    if l >= len(e):
        l = t
    d = e[l]
    p = l % d["row"]
    h = l % d["column"]
    g = d["matrix"][p][h]
    y = e[t]
    m = 3 % y["row"]
    v = 7 % y["column"]
    w = y["matrix"][m][v]
    b = i(f) + o(w)
    x = i(w) - o(f)
    return [s(a(i(f), o(f))), s(a(i(g), o(g))), s(a(i(w), o(w))), s(a(b, x))]

def i(e):
    return int(e.split(",")[0])

def o(e):
    return int(e.split(",")[1])

def a(e, t):
    return str(e) + "^⁣^" + str(t)

def s(e):
    t = 0
    n = len(e)
    for r in range(n):
        t = u(31 * t + ord(e[r]))
    return t

def u(e):
    t = -2147483648
    n = 2147483647
    if e > n:
        return t + (e - n) % (n - t + 1) - 1
    if e < t:
        return n - (t - e) % (n - t + 1) + 1
    return e

def c(e, t):
    return s(e + "⁣" + str(t))

def img_jj(e, t, n):
    return {"ca": r(e, t), "f": c(n, t)}

def md5(input_string):
    return hashlib.md5(input_string.encode()).hexdigest()

async def get_sign(xid, t):
    e = [
        {"alg": "md5", "salt": "KHBJ07an7ROXDoK7Db"},
        {"alg": "md5", "salt": "G6n399rSWkl7WcQmw5rpQInurc1DkLmLJqE"},
        {"alg": "md5", "salt": "JZD1A3M4x+jBFN62hkr7VDhkkZxb9g3rWqRZqFAAb"},
        {"alg": "md5", "salt": "fQnw/AmSlbbI91Ik15gpddGgyU7U"},
        {"alg": "md5", "salt": "/Dv9JdPYSj3sHiWjouR95NTQff"},
        {"alg": "md5", "salt": "yGx2zuTjbWENZqecNI+edrQgqmZKP"},
        {"alg": "md5", "salt": "ljrbSzdHLwbqcRn"},
        {"alg": "md5", "salt": "lSHAsqCkGDGxQqqwrVu"},
        {"alg": "md5", "salt": "TsWXI81fD1"},
        {"alg": "md5", "salt": "vk7hBjawK/rOSrSWajtbMk95nfgf3"}
    ]
    md5_hash = f"YvtoWO6GNHiuCl7xundefinedmypikpak.com{xid}{t}"
    for item in e:
        md5_hash += item["salt"]
        md5_hash = md5(md5_hash)
    return md5_hash

async def get_mail():
    json_data = {
        "min_name_length": 10,
        "max_name_length": 10
    }
    url = 'https://api.internal.temp-mail.io/api/v3/email/new'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json_data, ssl=False) as response:
            response_data = await response.json()
            mail = response_data['email']
        return mail

# 获取邮箱的验证码内容
async def get_code(mail, max_retries=10, delay=1):
    retries = 0
    while retries < max_retries:
        url = f'https://api.internal.temp-mail.io/api/v3/email/{mail}/messages'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False) as response:
                html = await response.json()
                if html:
                    text = (html[0])['body_text']
                    code = re.search('\\d{6}', text).group()
                    print(f'获取邮箱验证码:{code}')
                    return code
                else:
                    await asyncio.sleep(delay)
                    retries += 1
    print("获取邮箱邮件内容失败，未收到邮件...")
    return None

async def init(xid, mail):
    url = 'https://user.mypikpak.com/v1/shield/captcha/init'
    body = {
        "client_id": "YvtoWO6GNHiuCl7x",
        "action": "POST:/v1/auth/verification",
        "device_id": xid,
        "captcha_token": "",
        "meta": {
            "email": mail
        }
    }
    headers = {
        'host': 'user.mypikpak.com',
        'content-length': str(len(json.dumps(body))),
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'referer': 'https://pc.mypikpak.com',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'MainWindow Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'PikPak/2.3.2.4101 Chrome/100.0.4896.160 Electron/18.3.15 Safari/537.36',
        'accept-language': 'en',
        'content-type': 'application/json',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-client-id': 'YvtoWO6HNHiuG98x',
        'x-client-version': '2.3.2.4101',
        'x-device-id': xid,
        'x-device-model': 'electron%2F18.3.15',
        'x-device-name': 'PC-Electron',
        'x-device-sign': 'wdi10.ce8280a2dc704cd49f0be1c4eca40059xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'x-net-work-type': 'NONE',
        'x-os-version': 'Win64',
        'x-platform-version': '1',
        'x-provider-name': 'NONE',
        'x-sdk-version': '6.0.0'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as response:
            response_data = await response.json()
            return response_data

async def verification_code(mail):
    url = 'https://user.mypikpak.com/v1/auth/verification_code'
    body = {
        "client_id": "YvtoWO6GNHiuCl7x",
        "action": "REGISTER",
        "email": mail
    }
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN',
        'authorization': '',
        'content-length': '74',
        'content-type': 'application/json',
        'origin': 'https://pc.mypikpak.com',
        'referer': 'https://pc.mypikpak.com',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'x-client-id': 'YvtoWO6GNHiuCl7x',
        'x-client-version': '2.3.2.4101',
        'x-device-id': mail,
        'x-device-model': 'electron%2F18.3.15',
        'x-device-name': 'PC-Electron',
        'x-device-sign': 'wdi10.ce8280a2dc704cd49f0be1c4eca40059xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'x-net-work-type': 'NONE',
        'x-os-version': 'Win64',
        'x-platform-version': '1',
        'x-provider-name': 'NONE',
        'x-sdk-version': '6.0.0'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as response:
            response_data = await response.json()
            return response_data

async def verify_code(mail, code):
    url = 'https://user.mypikpak.com/v1/auth/verify_code'
    body = {
        "client_id": "YvtoWO6GNHiuCl7x",
        "email": mail,
        "code": code,
        "grant_type": "password"
    }
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN',
        'authorization': '',
        'content-length': '100',
        'content-type': 'application/json',
        'origin': 'https://pc.mypikpak.com',
        'referer': 'https://pc.mypikpak.com',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'x-client-id': 'YvtoWO6GNHiuCl7x',
        'x-client-version': '2.3.2.4101',
        'x-device-id': mail,
        'x-device-model': 'electron%2F18.3.15',
        'x-device-name': 'PC-Electron',
        'x-device-sign': 'wdi10.ce8280a2dc704cd49f0be1c4eca40059xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'x-net-work-type': 'NONE',
        'x-os-version': 'Win64',
        'x-platform-version': '1',
        'x-provider-name': 'NONE',
        'x-sdk-version': '6.0.0'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as response:
            response_data = await response.json()
            return response_data

async def accept_invite(mail):
    url = 'https://user.mypikpak.com/v1/team/invite/accept'
    body = {
        "client_id": "YvtoWO6GNHiuCl7x",
        "invite_code": INVITE_CODE,
        "email": mail
    }
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN',
        'authorization': '',
        'content-length': '100',
        'content-type': 'application/json',
        'origin': 'https://pc.mypikpak.com',
        'referer': 'https://pc.mypikpak.com',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'x-client-id': 'YvtoWO6GNHiuCl7x',
        'x-client-version': '2.3.2.4101',
        'x-device-id': mail,
        'x-device-model': 'electron%2F18.3.15',
        'x-device-name': 'PC-Electron',
        'x-device-sign': 'wdi10.ce8280a2dc704cd49f0be1c4eca40059xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'x-net-work-type': 'NONE',
        'x-os-version': 'Win64',
        'x-platform-version': '1',
        'x-provider-name': 'NONE',
        'x-sdk-version': '6.0.0'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as response:
            response_data = await response.json()
            return response_data

async def main():
    # 检查变量
    invite_code_list = check_env()
    
    for INVITE_CODE in invite_code_list:
        try:
            xid = str(uuid.uuid1()).replace("-", "")
            mail = await get_mail()
            print(f"生成邮箱: {mail}")

            # 初始化验证码请求
            await init(xid, mail)

            # 请求验证码
            await verification_code(mail)

            # 获取验证码
            code = await get_code(mail)
            if not code:
                raise Exception("获取验证码失败")

            # 验证验证码
            await verify_code(mail, code)

            # 接受邀请
            result = await accept_invite(mail)
            print_json(data=result)

            # 推送结果
            global PUSH_MSG
            PUSH_MSG += f'邮箱: {mail} 绑定成功\n'
            await push(PUSH_MSG)

        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
