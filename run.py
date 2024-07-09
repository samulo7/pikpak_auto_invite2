import json
import hashlib
import os
import re
import asyncio
import aiohttp
import uuid
from rich import print_json

DEBUG_MODE = True
PROXY = ''
PUSHPLUS_TOKEN = os.getenv('PUSHPLUS_TOKEN') or ''
INVITE_CODE = os.getenv('INVITE_CODE') or input('请输入邀请码: ')
PUSH_MSG = ''

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
            print(f"获取到邮箱: {mail}")  # Debug 信息
        return mail

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
                    print(f'获取邮箱验证码: {code}')  # Debug 信息
                    return code
                else:
                    print("没有获取到邮件内容，等待中...")  # Debug 信息
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
        'x-client-id': 'YvtoWO6GNHiuG98x',
        'x-client-version': '2.3.2.4101',
        'x-device-id': xid,
        'x-device-model': 'electron%2F18.3.15',
        'x-device-name': 'PC-Electron',
        'x-device-sign': await get_sign(xid, mail),
        'x-net-work-type': 'NONE',
        'x-os-version': 'win',
        'x-req-id': 'dcebe156-3292-42ea-8fa8-3c4c7c70f758',
        'x-soda-sdk-version': '2.3.2'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=body, headers=headers) as response:
            result = await response.json()
            if DEBUG_MODE:
                print_json(data=result)  # Debug 信息
            return result['captcha_token']

async def finish_captcha(captcha_token, verify_code, xid):
    url = 'https://user.mypikpak.com/v1/shield/captcha/verify'
    body = {
        "client_id": "YvtoWO6GNHiuCl7x",
        "device_id": xid,
        "captcha_token": captcha_token,
        "action": "POST:/v1/auth/verification",
        "meta": {
            "code": verify_code
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
        'x-os-version': 'win',
        'x-req-id': 'dcebe156-3292-42ea-8fa8-3c4c7c70f758',
        'x-soda-sdk-version': '2.3.2'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=body, headers=headers) as response:
            result = await response.json()
            if DEBUG_MODE:
                print_json(data=result)  # Debug 信息
            return result

async def main(invite_code):
    xid = str(uuid.uuid4())
    mail = await get_mail()
    print(f'邮箱: {mail}')
    captcha_token = await init(xid, mail)
    print(f'验证码TOKEN: {captcha_token}')
    verify_code = await get_code(mail)
    if verify_code:
        print(f'验证码: {verify_code}')
        verify_result = await finish_captcha(captcha_token, verify_code, xid)
        print(f'验证结果: {verify_result}')
    else:
        print("未能获取到验证码")
    # Place additional functionality here if needed

if __name__ == "__main__":
    invite_code_list = check_env()
    for invite_code in invite_code_list:
        asyncio.run(main(invite_code))
