import asyncio
import aiohttp
import json
import uuid

async def get_mail():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox") as response:
            response_data = await response.json()
            return response_data[0]

async def get_code(mail):
    try:
        login, domain = mail.split('@')
        url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                messages = await response.json()
                if messages:
                    message_id = messages[0]['id']
                    url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={message_id}"
                    async with session.get(url) as response:
                        message = await response.json()
                        for line in message['textBody'].split('\n'):
                            if 'Verification code:' in line:
                                return line.split(': ')[1].strip()
    except Exception as e:
        print(f"获取验证码时出错: {e}")
    return None

async def init(xid, mail):
    url = 'https://user.mypikpak.com/v1/auth/init'
    body = {
        "client_id": "YvtoWO6GNHiuCl7x",
        "email": mail,
        "device_id": xid
    }
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'x-client-id': 'YvtoWO6GNHiuCl7x',
        'x-client-version': '2.3.2.4101'
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
        'content-type': 'application/json',
        'x-client-id': 'YvtoWO6GNHiuCl7x',
        'x-client-version': '2.3.2.4101'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as response:
            response_data = await response.json()
            print(f"验证码请求响应: {response_data}")
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
        'content-type': 'application/json',
        'x-client-id': 'YvtoWO6GNHiuCl7x',
        'x-client-version': '2.3.2.4101'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as response:
            response_data = await response.json()
            print(f"验证验证码响应: {response_data}")
            return response_data

async def accept_invite(mail, INVITE_CODE):
    url = 'https://user.mypikpak.com/v1/team/invite/accept'
    body = {
        "client_id": "YvtoWO6GNHiuCl7x",
        "invite_code": INVITE_CODE,
        "email": mail
    }
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'x-client-id': 'YvtoWO6GNHiuCl7x',
        'x-client-version': '2.3.2.4101'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as response:
            response_data = await response.json()
            print(f"接受邀请响应: {response_data}")
            return response_data

async def main():
    INVITE_CODE = "YOUR_INVITE_CODE_HERE"  # Replace with actual invite code
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
        print(f"获取到的验证码: {code}")

        # 验证验证码
        await verify_code(mail, code)

        # 接受邀请
        result = await accept_invite(mail, INVITE_CODE)
        print(f"绑定成功: {result}")

    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
