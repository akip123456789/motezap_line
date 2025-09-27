from Lstep_utils.login import login,account_select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Lstep_utils.utils import click_items_within, check_last_item_within, has_items_within
import time




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


    return post_list

