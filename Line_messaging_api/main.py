import os
import requests
import json
import logging

# ログ設定
logger = logging.getLogger(__name__)

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
    logger.info(f"メッセージ送信開始 - グループID: {group_id}, メッセージ長: {len(message)}文字")
    
    # アクセストークンの取得
    if channel_access_token is None:
        channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    
    if not channel_access_token:
        logger.error("エラー: LINE_CHANNEL_ACCESS_TOKENが設定されていません")
        return False
    
    print("channel_access_token",channel_access_token)
    
    # メッセージが長い場合は分割
    if len(message) > 5000:
        logger.info("メッセージが長いため分割送信を実行します")
        return _send_long_message(group_id, message, channel_access_token)
    else:
        logger.info("単一メッセージとして送信します")
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
        
        logger.debug(f"送信ペイロード: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(
            'https://api.line.me/v2/bot/message/push',
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
        )
        
        logger.info(f"APIレスポンス - ステータスコード: {response.status_code}")
        logger.debug(f"レスポンスヘッダー: {dict(response.headers)}")
        logger.debug(f"レスポンス本文: {response.text}")
        
        if response.status_code == 200:
            logger.info("メッセージ送信成功")
            return True
        else:
            logger.error(f"メッセージ送信失敗 - ステータスコード: {response.status_code}, レスポンス: {response.text}")
            return False
        
    except Exception as e:
        logger.error(f"メッセージ送信エラー: {e}")
        import traceback
        logger.error(f"スタックトレース: {traceback.format_exc()}")
        return False

def _send_long_message(group_id: str, message: str, token: str) -> bool:
    """長いメッセージを分割して送信"""
    import time
    
    # 5000文字ずつに分割
    chunks = [message[i:i+5000] for i in range(0, len(message), 5000)]
    logger.info(f"メッセージを{len(chunks)}個のチャンクに分割しました")
    
    success_count = 0
    for i, chunk in enumerate(chunks):
        logger.info(f"チャンク {i+1}/{len(chunks)} を送信中...")
        if i > 0:
            time.sleep(0.5)  # 連続送信を避ける
        
        if _send_single_message(group_id, chunk, token):
            success_count += 1
            logger.info(f"チャンク {i+1} 送信成功")
        else:
            logger.error(f"チャンク {i+1} 送信失敗")
    
    logger.info(f"分割送信完了 - 成功: {success_count}/{len(chunks)}")
    return success_count == len(chunks)
