import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Database.db_setup import DB_Session
from Database.Models.BlockUser import BlockUser
from datetime import datetime
import pytz


def go_to_next_page_and_check(driver):
    """次のページに移動し、移動できたかどうかを返す"""
    wait = WebDriverWait(driver, 10)

    try:
        # ページネーション全体が表示されるまで待機
        pagination = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.pagination"))
        )

        # 「次へ」の li 要素を取得
        next_li = pagination.find_elements(By.XPATH, './/li[a[@rel="next"]] | .//li[@aria-label="次へ »"]')
        
        if not next_li:
            print("ページネーションが見つかりません")
            return False

        li = next_li[0]

        # 最終ページかどうか判定
        if "disabled" in li.get_attribute("class"):
            print("最終ページに到達しました")
            return False
        else:
            # 次のページリンクをクリック
            next_link = li.find_element(By.TAG_NAME, "a")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_link)
            next_link.click()
            print("次のページへ移動しました")
            return True

    except Exception as e:
        print(f"次ページ移動中にエラー: {e}")
        return False


def get_BlockUser(driver):
    user_list=[]
    session=DB_Session()
    wait = WebDriverWait(driver, 60)
    while True:
        rows = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#member_list tbody tr.friend-list-table-row"))
        )
        for row in rows:
            try:
                # 名前のaタグ（2番目のaが名前）
                name_link = row.find_elements(By.CSS_SELECTOR, "td.has_emoji a")[-1]
                name = name_link.text.strip()
                url = name_link.get_attribute("href")
                match = re.search(r'(?<=/detail/)\d+(?=$|[/?#])', url)
                if match:
                    menberid = match.group()

                # DB内にnameとmenberidが両方一致するレコードが存在する場合は保存しない
                exists = session.query(BlockUser).filter_by(username=name, user_menberid=menberid).first()
                if exists:
                    continue

                block_user = BlockUser(
                    username=name,
                    user_menberid=menberid,
                    time=datetime.now(pytz.timezone('Asia/Tokyo'))
                )
                session.add(block_user)
                user_list.append([name,menberid])
                

                
            except Exception as e:
                print("取得できない行がありました:", e)
        
        if not go_to_next_page_and_check(driver):
            break
    
    session.commit()

    session.close()
    return user_list

    