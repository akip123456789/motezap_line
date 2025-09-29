import time
from Database.db_setup import DB_Session
from Database.Models.BlockUser import BlockUser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pytz
from datetime import datetime

def get_shadow_root(driver, host):
    try:
        return host.shadow_root
    except Exception:
        return driver.execute_script("return arguments[0].shadowRoot", host)


def get_timeline(driver,user_list):
    db_sessions=DB_Session()
    send_message_list=[]
    wait = WebDriverWait(driver, 90)
    
    for user in user_list:
        driver.get(f"https://manager.linestep.net/line/detail/{user[1]}")
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
        date_str = tds[2].text.strip()  # 例: "2025/09/24(水) \n14:00 〜 14:30"
        # 日付部分のみ抽出（例: "2025/09/24"）
        date_only = date_str.split("(")[0].strip()
        date_obj = datetime.strptime(date_only, "%Y/%m/%d").date()
        today = datetime.now(pytz.timezone('Asia/Tokyo')).date()
        if date_obj < today:
            continue
        slot = tds[3].text.strip()

        


        send_message = BlockUser(
            username=user[0],
            user_menberid=user[1],
            time=datetime.now(pytz.timezone('Asia/Tokyo'))
        )
        db_sessions.add(send_message)
        send_message_list.append([user[0],user[1],calendar,date_str,slot])

    db_sessions.commit()
    db_sessions.close()
    return send_message_list