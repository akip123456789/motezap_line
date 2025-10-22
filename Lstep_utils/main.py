from Lstep_utils.login import login
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Lstep_utils.utils import click_items_within, check_last_item_within, has_items_within
import time
from Lstep_utils.get_BlockUser import get_BlockUser
from Lstep_utils.search import click_saved_search,day_set
from Lstep_utils.get_timeline import get_timeline
import pytz
from datetime import datetime,timedelta
from Lstep_utils.get_phonedata import get_phone_number
from Database.db_setup import DB_Session
from Database.Models.BookingCheck import Bookingcheck


def main_flow(hours):
    driver=login()
    driver.get("https://manager.linestep.net/line/visual")

    wait = WebDriverWait(driver, 10)
    post_list=[]

    # ul.list-group のロードを待つ
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list-group")))
    count = 0
    while True:
        click_items_within(driver,hours,count,post_list)
        if count==0:
            count+=29
        else:
            count+=30

        # 「続きをロード」ボタンをチェック
        load_more = driver.find_elements(By.CSS_SELECTOR, "ul.list-group > li.visual-list-loader")
        if load_more:
            # 最後のli要素が2時間以内の場合も「続きをロード」をクリック
            if check_last_item_within(driver,hours):
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more[0])
                load_more[0].click()
                time.sleep(2)  
                # 続きをロード後、2時間以内のli要素があるかチェック
                if not has_items_within(driver,hours):
                    # 2時間以内のli要素がなくなったらループを終了
                    break
            else:
                print("check_last_item_within is False")
                # 最後のli要素が2時間より前の場合はループを終了
                break
        else:
            print("load_more is not found")
            # 「続きをロード」ボタンがない場合はループを終了
            break

    driver.quit()
    return post_list



def main_BlockUser_flow():
    driver=login()
    driver.get("https://manager.linestep.net/line/show")
    click_saved_search(driver,keyword="予約ブロックした人")
    user_list=get_BlockUser(driver)
    send_message_list=get_timeline(driver,user_list)
    driver.quit()
    return send_message_list



def get_shadow_root(driver, host):
    try:
        return host.shadow_root
    except Exception:
        return driver.execute_script("return arguments[0].shadowRoot", host)


def main_booking_check():
    db_session=DB_Session()
    userdata=[]
    driver=login()
    driver.get("https://manager.linestep.net/line/show")
    click_saved_search(driver,keyword="送信済_予約確認ボタン")
    wait = WebDriverWait(driver, 60)


    now = datetime.now(pytz.timezone('Asia/Tokyo'))
    now_str = now.strftime("%Y/%m/%d")
    # 詳細検索で日付を選択
    memberid_list=day_set(driver,date=now_str)
    # memberidを取得
    for memberid in memberid_list:
        driver.get(f"https://manager.linestep.net/line/detail/{memberid[1]}")
        calendar_tab = wait.until(EC.element_to_be_clickable((By.ID, "salon_part_opener")))
        calendar_tab.click()

        # shadow host を取得
        host = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "v3-detail-salon")))
        shadow = get_shadow_root(driver, host)

        # 行を取得
        rows = driver.execute_script(
            "return arguments[0].querySelectorAll('tbody tr[data-item-id]')", shadow
        )

        tds = driver.execute_script("return arguments[0].querySelectorAll('td')", rows[0])
        calendar = tds[1].text.strip()
        date_str = tds[2].text.strip()
        start_time = ""
        if "\n" in date_str:
            parts = date_str.split("\n")
            if len(parts) > 1 and "〜" in parts[1]:
                start_time = parts[1].split("〜")[0].strip()
        slot = tds[3].text.strip()

        now = datetime.now(pytz.timezone('Asia/Tokyo'))
        # start_time は "HH:MM" と仮定
        start_dt = datetime.strptime(start_time, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day, tzinfo=now.tzinfo
        )
        diff = (start_dt - now).total_seconds() / 60  # 分単位
        # 現在時刻より未来で1時間(60分)以内かどうかチェック
        if 0 <= diff <= 60:
            print(f"start_time {start_time} は現在時刻の1時間以内です")
        else:
            print(f"start_time {start_time} は現在時刻の1時間以内ではありません")
            continue
            
        driver.get(f"https://manager.linestep.net/line/visual?show=detail&member={memberid[1]}")
        phone = get_phone_number(driver)
        print("電話番号:", phone)
        print("calendar",calendar)
        print("slot",slot)
        print("date_str",date_str)
        print("username",memberid[0])
        print("memberid",memberid[1])
        print("--------------------------------")
        userdata.append([memberid[0],memberid[1],calendar,date_str,slot,phone])
        db_session.add(Bookingcheck(memberid=memberid[1]))  

    db_session.commit()
    db_session.close()
    driver.quit()
    return userdata


