import asyncio
import aiohttp
import json
import uuid

async def get_mail():
    url = "https://api.tikhub.io/api/v1/temp_mail/v1/get_temp_email_address"
    headers = {
        "cf-cache-status": "DYNAMIC",
        "cf-ray": "8a04ad452b338502-HKG",
        "content-length": "358",
        "content-type": "application/json",
        "date": "Tue,09 Jul 2024 01:52:49 GMT",
        "nel": '{"success_fraction":0,"report_to":"cf-nel","max_age":604800}',
        "report-to": '{"endpoints":[{"url":"https://a.nel.cloudflare.com/report/v4?s=jIw5I4w8t58DHdNyXPW1JGHdala7MKTwZT3cyYYv1hGo6eGxdCL3IGfuL/Jb9c/vaepb/Mtzve+aQAyByrdpf8Vat6McQR2qnnwpBaQSTFvWh3Zq8DXeXvL3d1E27C8="}],"group":"cf-nel","max_age":604800}',
        "server": "cloudflare"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                email = data.get("email")
                if email:
                    print(f"生成邮箱: {email}")
                    return email
                else:
                    print("获取邮箱失败")
                    return None
            else:
                print(f"请求失败，状态码: {response.status}")
                return None

async def get_code(mail):
    try:
        login, domain = mail.split('@')
        url = f"https://api.tikhub.io/api/v1/temp_mail/v1/get_email/{mail}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                messages = await response.json()
                if messages:
                    message_id = messages[0]['id']
                    url = f"https://api.tikhub.io/api/v1/temp_mail/v1/read_email/{message_id}"
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
