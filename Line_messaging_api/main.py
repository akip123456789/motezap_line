import os
import requests
import json

def send_message(group_id: str, message: str, channel_access_token: str = None) -> bool:
    """
    指定されたグループにメッセージを送信する
    
    Args:
        group_id (str): 送信先グループのID
        message (str): 送信するメッセージ
        channel_access_token (str): LINEチャンネルのアクセストークン（省略時は環境変数から取得）
        
    Returns:
        bool: 送信成功の場合True、失敗の場合False
    """
    # アクセストークンの取得
    if channel_access_token is None:
        channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    
    if not channel_access_token:
        print("エラー: LINE_CHANNEL_ACCESS_TOKENが設定されていません")
        return False
    
    # メッセージが長い場合は分割
    if len(message) > 5000:
        return _send_long_message(group_id, message, channel_access_token)
    else:
        return _send_single_message(group_id, message, channel_access_token)

def _send_single_message(group_id: str, message: str, token: str) -> bool:
    """単一メッセージを送信"""
    try:
        payload = {
            "to": group_id,
            "messages": [{"type": "text", "text": message}]
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            'https://api.line.me/v2/bot/message/push',
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
        )
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"メッセージ送信エラー: {e}")
        return False

def _send_long_message(group_id: str, message: str, token: str) -> bool:
    """長いメッセージを分割して送信"""
    import time
    
    # 5000文字ずつに分割
    chunks = [message[i:i+5000] for i in range(0, len(message), 5000)]
    
    success_count = 0
    for i, chunk in enumerate(chunks):
        if i > 0:
            time.sleep(0.5)  # 連続送信を避ける
        
        if _send_single_message(group_id, chunk, token):
            success_count += 1
    
    return success_count == len(chunks)
