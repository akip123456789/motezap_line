from Lstep_utils.login import login
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import time

def get_field_value(driver, label_text, timeout=20):
    wait = WebDriverWait(driver, timeout)

    # 1) 「プロフィール」グループのテーブルが出るまで待機
    #    （ラベルに「プロフィール」を含む group-box を基点にする）
    profile_table = wait.until(EC.presence_of_element_located((
        By.XPATH,
        "//div[contains(@class,'group-box')][.//div[contains(@class,'group-label') and normalize-space()='プロフィール']]"
        "//table[contains(@class,'table-var-list')]"
    )))

    # 2) 指定ラベル(th)の右隣(td)内 <div> テキストを取得
    try:
        value_el = profile_table.find_element(
            By.XPATH,
            f".//tr[.//th[normalize-space()='{label_text}']]//td//div"
        )
        return value_el.text.strip()
    except Exception:
        # フォールバック：ページ全体から探す（DOM構造が微妙に違う場合に対応）
        try:
            value_el = wait.until(EC.presence_of_element_located((
                By.XPATH,
                f"//table[contains(@class,'table-var-list')]"
                f"//tr[.//th[normalize-space()='{label_text}']]//td//div"
            )))
            return value_el.text.strip()
        except TimeoutException:
            return "電話番号なし"  # 見つからない場合は ""

def get_phone_number(driver):
    return get_field_value(driver, "電話番号")

