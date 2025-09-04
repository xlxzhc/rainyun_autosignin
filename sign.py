#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
环境变量：

`yyqd`: 雨云的**账户**和**密码**，用 `&` 分隔。多账户用 `#` 分隔。
`CAPTCHA_URL`: 验证码识别接口的 URL。
`CAPTCHA_METHOD`: 请求验证码接口使用的方法，`GET` 或 `POST`。
`CAPTCHA_DATA`: 发送到验证码接口的 JSON 数据。

定时：建议每天执行一次
"""

import requests, json, os, time, random
from dataclasses import dataclass

try:
    from notify import send
except ImportError:
    print("通知服务加载失败，请检查notify.py是否存在")
    exit(1)

@dataclass
class UserInfo:
    name: str
    email: str
    points: int
    last_ip: str
    last_login_area: str

class RainyunAPI:
    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None
    
    def get_slide_verify(self):
        # 决策理由：根据用户要求，移除默认验证码服务，强制用户配置自定义服务。
        captcha_url = os.getenv("CAPTCHA_URL")
        captcha_method = os.getenv("CAPTCHA_METHOD")
        captcha_data_str = os.getenv("CAPTCHA_DATA")

        if not all([captcha_url, captcha_method, captcha_data_str]):
            print("错误: 必须配置 CAPTCHA_URL, CAPTCHA_METHOD, 和 CAPTCHA_DATA 环境变量。")
            return "", ""

        try:
            # 决策理由：确保 CAPTCHA_DATA 是合法的 JSON 格式。
            captcha_data = json.loads(captcha_data_str.replace("'", "\""))
        except json.JSONDecodeError:
            print("错误: CAPTCHA_DATA 环境变量不是有效的 JSON 字符串。")
            return "", ""

        for i in range(3):
            try:
                if captcha_method.upper() == "POST":
                    res = self.session.post(captcha_url, json=captcha_data, timeout=20)
                else: # 默认为 GET
                    res = self.session.get(captcha_url, params=captcha_data, timeout=20)
                
                res.raise_for_status()
                data = res.json()

                if data.get("data") and data.get("data").get("ticket"):
                    return data["data"].get('ticket'), data["data"].get('randstr')
                else:
                    print(f"第{i + 1}次验证码获取失败: 响应中缺少 ticket。响应内容: {res.text}")

            except Exception as e:
                print(f"第{i + 1}次验证码获取失败: {e}")
            
            if i < 2:
                time.sleep(2)
        return "", ""

    def login(self, username, password):
        try:
            r = self.session.post("https://api.v2.rainyun.com/user/login",
                headers={"Content-Type": "application/json"},
                json={"field": username, "password": password})
            self.csrf_token = r.cookies.get('X-CSRF-Token')
            return bool(self.csrf_token)
        except:
            return False

    def get_user_info(self):
        if not self.csrf_token:
            return None
        try:
            r = self.session.get("https://api.v2.rainyun.com/user/?no_cache=false",
                headers={"Content-Type": "application/json", 'x-csrf-token': self.csrf_token})
            d = r.json()['data']
            return UserInfo(d['Name'], d['Email'], d['Points'], d['LastIP'], d['LastLoginArea'])
        except:
            return None

    def sign_in(self, ticket, randstr):
        if not self.csrf_token:
            return False, "未获取到csrf_token"
        try:
            r = self.session.post("https://api.v2.rainyun.com/user/reward/tasks",
                headers={'x-csrf-token': self.csrf_token},
                json={"task_name": "每日签到", "verifyCode": "",
                     "vticket": ticket, "vrandstr": randstr})
            ret = r.json()
            return ret["code"] == 200, ret.get("message", "未知错误")
        except Exception as e:
            return False, str(e)

def process_account(account):
    try:
        username, password = account.split('&')
    except:
        return "\n账户格式错误"

    api = RainyunAPI()
    if not api.login(username, password):
        return f'\n【用户名】{username}\n【签到状态】登录失败'

    delay = random.randint(20, 30)
    time.sleep(delay)
    
    ticket, randstr = api.get_slide_verify()
    if not ticket:
        return f'\n【用户名】{username}\n【签到状态】验证失败'

    user_info = api.get_user_info()
    if not user_info:
        return f'\n【用户名】{username}\n【签到状态】获取信息失败'

    success, sign_message = api.sign_in(ticket, randstr)
    if success:
        sign_message = "签到成功"
        
    return (f'\n【用户名】{username}\n'
            f'【电子邮件】{user_info.email}\n'
            f'【延迟时间】{delay}秒\n'
            f'【签到状态】{sign_message}\n'
            f'【剩余积分】{user_info.points}\n'
            f'【最后登录ip】{user_info.last_ip}\n'
            f'【最后登录地址】{user_info.last_login_area}')

def main():
    creds = os.getenv("yyqd")
    if not creds:
        print("错误：必须设置 `yyqd` 环境变量。")
        return

    results = [process_account(acc) for acc in creds.split('#')]
    msg = "-"*45 + "\n".join(results)
    print("###雨云签到###\n\n", msg)
    send("雨云签到", msg)

if __name__ == '__main__':
    main()