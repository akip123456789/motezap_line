from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import re
from Database.db_setup import DB_Session
from Database.Models.BookingCheck import Bookingcheck
import time
def click_saved_search(driver,keyword):
    

    wait = WebDriverWait(driver, 20)
    primary = (By.CSS_SELECTOR, "button.btn.btn-primary[data-target='#newFunnelSelectorModal']")
    btn = wait.until(EC.element_to_be_clickable(primary))
    btn.click()

    host = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "v3-item-selector[itemtype='funnel']")))
    try:
        shadow = host.shadow_root
    except Exception:
        shadow = driver.execute_script("return arguments[0].shadowRoot", host)

    # --- 検索ボックスを取得（hidden なら表示状態になるまで待つ） ---
    search_input = wait.until(
        lambda d: shadow.find_element(By.CSS_SELECTOR, "div.searchbox input[placeholder='カスタム検索名を入力']")
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", search_input)

    # --- 値を直接設定して input/change イベントを発火 ---
    driver.execute_script("""
    const el = arguments[0], val = arguments[1];
    el.focus();
    el.value = val;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    """, search_input, keyword)
    
    li_elements = wait.until(
    lambda d: shadow.find_elements(By.CSS_SELECTOR, "ul > li")
    )
    for li in li_elements:
        text = li.text.strip()
        if text == keyword:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", li)
            li.click()
            break

    # モーダルウインドウが閉じられるまで待つ
    wait = WebDriverWait(driver, 60)
    # モーダルが非表示になるまで待機
    wait.until(EC.invisibility_of_element_located((By.ID, "newFunnelSelectorModal")))
    return


def _fill_date(driver, input_elem, value_str):
    """DatePickerのinputに値を入れて、必要なイベントを発火させる"""
    # 1) クリア（✕アイコンがあればクリック）
    try:
        wrap = input_elem.find_element(By.XPATH, "./ancestor::*[contains(@class,'dp__input_wrap')]")
        clear_btn = wrap.find_element(By.CSS_SELECTOR, "svg.dp__clear_icon")
        driver.execute_script("arguments[0].click();", clear_btn)
    except Exception:
        pass  # なければ無視

    # 2) 直接入力（フォールバック込み）
    input_elem.click()
    input_elem.send_keys(Keys.CONTROL, "a")
    input_elem.send_keys(value_str)
    # Enterで確定させるUIもある
    input_elem.send_keys(Keys.ENTER)

    # 3) Vue/React向けにinput/changeイベントも確実に飛ばす
    driver.execute_script("""
        const el = arguments[0], val = arguments[1];
        if (el.value !== val) el.value = val;
        el.dispatchEvent(new Event('input', {bubbles:true}));
        el.dispatchEvent(new Event('change', {bubbles:true}));
        el.blur();
    """, input_elem, value_str)

def select_date_range(driver, start_date_str, end_date_str, timeout=10):
    """
    例: select_date_range(driver, "2025/10/01", "2025/10/15")
    フォーマットはページと同じ 'YYYY/MM/DD' を想定
    """
    wait = WebDriverWait(driver, timeout)

    # 「日付」トグルが必要なら、先にONにする（既にONなら何もしない）
    try:
        label_date = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//label[.//span[normalize-space()='日付']]")
        ))
        checkbox = label_date.find_element(By.XPATH, ".//input[@type='checkbox']")
        checked = checkbox.get_attribute("checked")
        if not checked:
            label_date.click()
    except Exception:
        pass  # トグルが無い/既に有効ならスキップ

    # 開始入力
    start_input = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//input[@placeholder='開始日付' and contains(@class,'dp__input')]")
    ))
    _fill_date(driver, start_input, start_date_str)

    # 終了入力
    end_input = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//input[@placeholder='終了日付' and contains(@class,'dp__input')]")
    ))
    _fill_date(driver, end_input, end_date_str)

    time.sleep(5)

    return


def wait_modal_closed(driver, timeout=20, root=None):
    """
    Vue Final Modal系のモーダルが閉じる(非表示 or DOMから消える)まで待機する
    - root: 検索コンテキスト（ShadowRootなど）。指定しなければdriver全体。
    """
    wait = WebDriverWait(driver, timeout, poll_frequency=0.2)
    # よく使われるセレクタ候補
    locators = [
        (By.CSS_SELECTOR, ".member-query-modal"),
        (By.CSS_SELECTOR, ".vfm__content"),
    ]

    # まず「存在する/表示されている」状態を一瞬だけ待つ（既に閉じているケースはスキップ）
    try:
        for by, sel in locators:
            try:
                if root:
                    wait.until(lambda d: any(el.is_displayed() for el in root.find_elements(by, sel)))
                else:
                    wait.until(EC.visibility_of_element_located((by, sel)))
                break  # どれか1つ見つかれば次へ
            except TimeoutException:
                continue
    except Exception:
        pass  # そもそも開いていなかった

    # 「見えなくなる/消える」まで待つ
    def invisible():
        for by, sel in locators:
            try:
                if root:
                    els = root.find_elements(by, sel)
                else:
                    els = driver.find_elements(by, sel)
                # 要素が存在しない ＝ 閉じた
                if not els:
                    return True
                # 1つでも表示中ならまだ閉じていない
                if any(el.is_displayed() for el in els):
                    return False
                # すべて非表示ならOK
                return True
            except StaleElementReferenceException:
                return True  # DOMから除去された＝閉じた扱い
        return False

    wait.until(lambda d: invisible())


def day_set(driver,date):
    wait = WebDriverWait(driver, 30)
    host = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "simple-member-query")))
    shadow = host.shadow_root  # Selenium 4

    # 2) Shadow DOM 内の button 群を取得してテキストで絞る
    def find_detail_button(_):
        try:
            buttons = shadow.find_elements(By.CSS_SELECTOR, "button")
            for b in buttons:
                if b.text.strip() == "詳細検索":
                    return b
        except Exception:
            return None
        return None

    btn = wait.until(find_detail_button)
    btn.click()

    select_date_range(driver, date, date)

    wait = WebDriverWait(driver, 10)
    button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@data-testid='linyBtn' and normalize-space()='決定する']")
        )
    )
    button.click()
    wait_modal_closed(driver, timeout=20) 
    
    links = driver.find_elements(By.XPATH, "//a[contains(@href, '/line/detail/')]")

    user_list = []  # [username, id] の配列を格納
    seen_ids = set()

    db_session = DB_Session()

    for link in links:
        href = link.get_attribute("href")
        text = link.text.strip()  # 名前
        match = re.search(r"/detail/(\d+)", href)
        if match:
            user_id = match.group(1)
            # 重複を避けて保存
            for link_info in [[text, user_id] for link in links if (href := link.get_attribute("href")) and (text := link.text.strip()) and (match := re.search(r"/detail/(\d+)", href)) and (user_id := match.group(1))]:
                print("link_info",link_info)
                username, user_id = link_info
                if user_id not in seen_ids:
                    # DBに既に存在するかチェック
                    exists = db_session.query(Bookingcheck).filter_by(memberid=user_id).first()
                    if not exists:
                        user_list.append([username, user_id])
                        seen_ids.add(user_id)


    db_session.close()
    return user_list

