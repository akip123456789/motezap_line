from Lstep_utils.main import main_flow
from Line_messaging_api.main import send_message
import os
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from Lstep_utils.main import main_BlockUser_flow

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

line_group_id=os.getenv("LINE_GROUP_ID")
line_channel_access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def send_notification():
    """未返信ユーザーの通知を送信する関数"""
    try:
        logger.info("未返信ユーザーのチェックを開始します")
        post_list=main_flow(hours=10)
        message="[通知]未返信のユーザー\n"    
        for post in post_list:        
            message+=f"名前:{post[0]}\n個別トークURL:{post[1]}\n\n"
            if len(message) > 4600:
                send_message(line_group_id,message,line_channel_access_token)
                message="[通知]未返信のユーザー（続き）\n"

        if len(message) > len("[通知]未返信のユーザー（続き）\n"):
            send_message(line_group_id,message,line_channel_access_token)
        
        logger.info("未返信ユーザーのチェックが完了しました")
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")

    
def send_notification_BlockUser():
    """ブロックユーザーの通知を送信する関数"""
    try:
        logger.info("ブロックユーザーのチェックを開始します")
        user_list=main_BlockUser_flow()
        message="[通知]新規にブロックされたユーザー\n"
        for user in user_list:
            message+=f"{user[0]}({user[1]})\nカレンダー:\n{user[2]}\n日付:\n{user[3]}\n予約枠:\n{user[4]}\n\n"
            if len(message) > 4600:
                send_message(line_group_id,message,line_channel_access_token)
                message="[通知]新規にブロックされたユーザー（続き）\n"
        if len(message) > len("[通知]新規にブロックされたユーザー（続き）\n"):
            send_message(line_group_id,message,line_channel_access_token)
        logger.info("新規にブロックされたユーザーのチェックが完了しました")

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        logger.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    # スケジューラーを設定
    scheduler = BlockingScheduler()
    
    # 15分ごとに実行するように設定
    scheduler.add_job(
        send_notification,
        trigger=IntervalTrigger(minutes=15),
        id='notification_job',
        name='未返信ユーザー通知',
        replace_existing=True
    )

    scheduler.add_job(
        send_notification_BlockUser,
        trigger=IntervalTrigger(minutes=15),
        id='notification_BlockUser_job',
        name='新規にブロックされたユーザー通知',
        replace_existing=True
    )
    
    logger.info("スケジューラーを開始します（15分ごとに実行）")
    logger.info("新規にブロックされたユーザーのチェックを開始します（15分ごとに実行）")
    logger.info("停止するには Ctrl+C を押してください")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("スケジューラーを停止します")
        scheduler.shutdown()
