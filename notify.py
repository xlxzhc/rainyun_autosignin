#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import json

# 决策理由：根据用户要求，重构通知服务，移除 ServerChan，
# 并实现 PushPlus 和 Telegram Bot 两种新的通知渠道，为用户提供更多选择。
# 脚本会按顺序检查环境变量，使用第一个被配置的渠道发送通知。

def send_pushplus(token: str, title: str, content: str) -> bool:
    """
    通过 PushPlus (推送加) 发送通知。
    """
    url = "http://www.pushplus.plus/send"
    payload = {
        "token": token,
        "title": title,
        "content": content.replace('\n', '<br>'),  # PushPlus 使用 HTML 换行
        "template": "markdown" # 决策理由：使用 Markdown 模板以获得更好的格式支持。
    }
    try:
        response = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'}, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get("code") == 200:
            print("PushPlus 通知发送成功。")
            return True
        else:
            print(f"PushPlus 通知发送失败: {result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"请求 PushPlus API 时发生错误: {e}")
        return False

def send_telegram(token: str, chat_id: str, title: str, content: str) -> bool:
    """
    通过 Telegram Bot 发送通知。
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    # 决策理由：使用 MarkdownV2 格式，并正确转义，以防止因特殊字符导致的发送失败。
    escaped_content = content.replace('.', '\\.').replace('-', '\\-').replace('!', '\\!')
    payload = {
        'chat_id': chat_id,
        'text': f'*{title}*\n\n{escaped_content}',
        'parse_mode': 'MarkdownV2'
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get("ok"):
            print("Telegram 通知发送成功。")
            return True
        else:
            print(f"Telegram 通知发送失败: {result.get('description', '未知错误')}")
            return False
    except Exception as e:
        print(f"请求 Telegram API 时发生错误: {e}")
        return False

def send(title: str, content: str) -> None:
    """
    统一的发送函数，按顺序尝试不同的通知渠道。
    """
    push_plus_token = os.getenv("PUSH_PLUS_TOKEN")
    tg_bot_token = os.getenv("TG_BOT_TOKEN")
    tg_user_id = os.getenv("TG_USER_ID")

    if push_plus_token:
        print("检测到 PushPlus 配置，尝试发送通知...")
        if send_pushplus(push_plus_token, title, content):
            return # 发送成功后即返回

    if tg_bot_token and tg_user_id:
        print("检测到 Telegram Bot 配置，尝试发送通知...")
        if send_telegram(tg_bot_token, tg_user_id, title, content):
            return # 发送成功后即返回

    print("未配置任何有效的通知渠道，跳过发送。")

if __name__ == '__main__':
    # 用于直接运行测试
    # 需要设置相应的环境变量
    # export PUSH_PLUS_TOKEN="your_pushplus_token"
    # export TG_BOT_TOKEN="your_tg_bot_token"
    # export TG_USER_ID="your_tg_user_id"
    send('测试标题', '这是一条测试内容。\n- 延迟时间: 25秒\n- 剩余积分: 10000')