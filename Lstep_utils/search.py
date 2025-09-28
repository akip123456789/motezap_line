from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException
import time



def click_saved_search(driver):
    keyword = "予約ブロックした人"

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