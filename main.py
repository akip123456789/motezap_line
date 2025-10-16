from Lstep_utils.main import main_flow,main_BlockUser_flow,main_booking_check
from Line_messaging_api.main import send_message
import os
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from clear_tmp import clear_tmp
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
        clear_tmp()
        post_list=main_flow(hours=10)
        message="未返信のユーザー\n"    
        for post in post_list:        
            message+=f"\n名前:{post[0]}\n個別トークURL:{post[1]}"
            if len(message) > 4600:
                send_message(line_group_id,message,line_channel_access_token)
                message="未返信のユーザー（続き）\n"

        if len(message) > len("未返信のユーザー（続き）\n"):
            send_message(line_group_id,message,line_channel_access_token)
        
        logger.info("未返信ユーザーのチェックが完了しました")
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")

    
def send_notification_BlockUser():
    """ブロックユーザーの通知を送信する関数"""
    try:
        logger.info("ブロックユーザーのチェックを開始します")
        clear_tmp()
        user_list=main_BlockUser_flow()
        message="新規にブロックされたユーザー\n"
        for user in user_list:
            message+=f"\n{user[0]}({user[1]})\nカレンダー:\n{user[2]}\n日付:\n{user[3]}\n予約枠:\n{user[4]}"
            if len(message) > 4600:
                send_message(line_group_id,message,line_channel_access_token)
                message="新規にブロックされたユーザー（続き）\n"
        if len(message) > len("新規にブロックされたユーザー（続き）\n"):
            send_message(line_group_id,message,line_channel_access_token)
        logger.info("新規にブロックされたユーザーのチェックが完了しました")

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        logger.error(f"エラーが発生しました: {e}")


def send_notification_booking_check():
    """予約確認ボタンが付与されたユーザーの通知を送信する関数"""
    try:
        logger.info("予約確認ボタンが付与されたユーザーのチェックを開始します")
        clear_tmp()

        logger.info("予約確認データを取得中...")
        userdata=main_booking_check()
        logger.info(f"取得したユーザーデータ数: {len(userdata)}")
        
        if not userdata:
            logger.info("送信するデータがありません")
            return
        
        message="タグ名「送信済_予約確認ボタン」が付与されました\n"
        message_count = 0
        
        for i, user in enumerate(userdata):
            logger.debug(f"ユーザー {i+1}/{len(userdata)} を処理中: {user[0]}")
            user_message = f"\n名前:{user[0]}\n個別トークURL:{user[1]}\nカレンダー:{user[2]}\n日付:{user[3]}\n予約枠:{user[4]}\n電話番号:{user[5]}"
            message += user_message
            
            if len(message) > 4600:
                logger.info(f"メッセージが長くなったため送信します（{len(message)}文字）")
                success = send_message(line_group_id, message, line_channel_access_token)
                if success:
                    message_count += 1
                    logger.info(f"メッセージ {message_count} 送信成功")
                else:
                    logger.error(f"メッセージ {message_count + 1} 送信失敗")
                message="タグ名「送信済_予約確認ボタン」が付与されたユーザー（続き）\n"
        
        # 残りのメッセージを送信
        if len(message) > len("タグ名「送信済_予約確認ボタン」が付与されたユーザー（続き）\n"):
            logger.info(f"最終メッセージを送信します（{len(message)}文字）")
            success = send_message(line_group_id, message, line_channel_access_token)
            if success:
                message_count += 1
                logger.info(f"最終メッセージ送信成功")
            else:
                logger.error("最終メッセージ送信失敗")
        
        logger.info(f"予約確認ボタンが付与されたユーザーのチェックが完了しました（送信メッセージ数: {message_count}）")
        
    except Exception as e:
        import traceback
        logger.error(f"予約確認通知でエラーが発生しました: {e}")
        logger.error(f"スタックトレース: {traceback.format_exc()}")
    return


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

    scheduler.add_job(
        send_notification_booking_check,
        trigger=IntervalTrigger(minutes=15),
        id='notification_booking_check_job',
        name='タグ名「送信済_予約確認ボタン」が付与されたユーザー通知',
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
