from datetime import datetime, timedelta
import time
from selenium.webdriver.common.by import By
import re
import traceback
from Lstep_utils.get_latest_message import get_latest_message
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Llm_utils.main import QuestionClassifier
from Database.db_setup import DB_Session
from Database.Models.Posted import Posted
import pytz

def parse_time_str(t_str):
    """
    li 内の時間表示を datetime に変換する
    表示が "HH:MM" の場合を想定（例: "14:52"）
    """
    try:
        now = datetime.now(pytz.timezone('Asia/Tokyo'))
        hour, minute = map(int, t_str.strip().split(":"))
        # 今日の日付と組み合わせる
        candidate = datetime(now.year, now.month, now.day, hour, minute)
        # もし未来になってしまう場合（例: 日付をまたいだケース）は前日とみなす
        if candidate > now:
            candidate -= timedelta(days=1)
        return candidate
    except Exception:
        return None

def click_items_within(driver,hours,count,post_list):
    session=DB_Session()

    now = datetime.now(pytz.timezone('Asia/Tokyo'))
    two_hours_ago = now - timedelta(hours=hours)

    while True:
        li_elements = driver.find_elements(By.CSS_SELECTOR, "ul.list-group > li.list-group-item.visual-list-item")
        if len(li_elements) == 20:
            continue
        else:
            break

    for i,li in enumerate(li_elements):
        if count>=29:
            if i <= count:
                continue
        try:
            time_el = WebDriverWait(li, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".visual-list-status .visual-list-time"))
            )
            time_str = time_el.text.strip()
            msg_time = parse_time_str(time_str)
            if msg_time and msg_time >= two_hours_ago:
                # 2時間以内ならクリック
                driver.execute_script("arguments[0].scrollIntoView(true);", li)
                li.click()
                time.sleep(1)  # 必要に応じて待機
            else:
                break
            
            # visual-list-nameを取得
            name_el = li.find_element(By.CSS_SELECTOR, ".visual-list-name")
            visual_list_name = name_el.text.strip()
            print(f"visual-list-name: {visual_list_name}")    
            # 個別トークから最新のメッセージを取得
            try:
                info = get_latest_message(driver)
                # 疑問系か否か
                if info["type"] == "User":
                    text = info["text"]
                    print("text:", text[:10])
                    classifier = QuestionClassifier()
                    rule_result = classifier.is_question_by_rules(text)
                    if rule_result['is_question']:
                        current_url=driver.current_url
                        match = re.search(r"[?&]member=([^&#]+)", current_url)
                        member_value = match.group(1) if match else None
                        
                        # 同じ組み合わせのユーザーが存在するか確認
                        existing_posted = session.query(Posted).filter_by(
                            username=info["username"],
                            user_menberid=member_value
                        ).first()
                        if existing_posted:
                            # 1時間以内か確認
                            current_time = info.get("created_at", datetime.now(pytz.timezone('Asia/Tokyo')))
                            if (current_time - existing_posted.created_at).total_seconds() > 1 * 3600:
                                # 1時間以内でなければcreated_atのみ上書き
                                existing_posted.created_at = current_time
                                session.commit()
                                post_list.append([visual_list_name,current_url])
                                continue
                        else:
                            posted = Posted(
                                username=info["username"],
                                user_menberid=member_value,
                                created_at=info.get("created_at", datetime.now(pytz.timezone('Asia/Tokyo')))
                            )
                            session.add(posted)
                            session.commit()
                            post_list.append([visual_list_name,current_url])
                            continue
                    else:
                        continue
                    
                # 疑問系の場合リストに含める
                else:
                    print("ユーザーメッセージは存在しない。")
   




            except Exception as msg_error:
                print("click_items_within_error:Exception",msg_error)
                print("click_items_within_error:traceback",traceback.print_exc())
                continue



            print("現在のURL:", driver.current_url)


        except Exception as e:
            li_elements_total=len(li_elements)-21
            if i >= li_elements_total:
                break
            else:
                print("click_items_within_error:Exception",e)
                print("click_items_within_error:traceback",traceback.print_exc())
                continue
        
        
        session.close()


        # 2時間より前はスキップ


def check_last_item_within(driver,hours):
    """
    ul内の最後のli要素が2時間以内かどうかをチェック
    """
    now = datetime.now(pytz.timezone('Asia/Tokyo'))
    two_hours_ago = now - timedelta(hours=hours)
    
    li_elements = driver.find_elements(By.CSS_SELECTOR, "ul.list-group > li.list-group-item.visual-list-item")
    
    if not li_elements:
        return False
    
    # 最後のli要素の時間をチェック
    last_li = li_elements[-21]
    try:
        time_el = last_li.find_element(By.CSS_SELECTOR, ".visual-list-status .visual-list-time")
        time_str = time_el.text.strip()
        msg_time = parse_time_str(time_str)
        return msg_time and msg_time >= two_hours_ago
    except Exception as e:
        print("error:Exception",e)
        print("error:traceback",traceback.print_exc())
        return False



def has_items_within(driver,hours):
    """
    現在のページに2時間以内のli要素があるかどうかをチェック
    """
    now = datetime.now(pytz.timezone('Asia/Tokyo'))
    two_hours_ago = now - timedelta(hours=hours)
    
    li_elements = driver.find_elements(By.CSS_SELECTOR, "ul.list-group > li.list-group-item.visual-list-item")
    
    for li in li_elements:
        try:
            time_el = li.find_element(By.CSS_SELECTOR, ".visual-list-status .visual-list-time")
            time_str = time_el.text.strip()
            msg_time = parse_time_str(time_str)
            if msg_time and msg_time >= two_hours_ago:
                return True
        except:
            continue
    
    return False