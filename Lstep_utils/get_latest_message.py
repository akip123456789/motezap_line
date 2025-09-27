from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_latest_message(driver, timeout=15):
    wait = WebDriverWait(driver, timeout)

    # スクロール可能な領域までロード完了を待機
    inner = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".nano-wrapper #nano-messages .nano-content .nano-inner"))
    )

    # 念のため最下部までスクロール（新着が仮想リストの場合に備える）
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", 
                          driver.find_element(By.CSS_SELECTOR, ".nano-wrapper #nano-messages .nano-content"))

    # 「表示されている」wrapper のうち、メッセージ（user/system）を含むものだけを抽出
    # XPath で最後の要素を直接取ると、非表示行に当たる可能性があるため、一覧→後ろから探索します
    wrappers = inner.find_elements(By.XPATH,
        ".//div[contains(@class,'wrapper')][.//div[contains(@class,'user-message')] "
        "or .//div[contains(@class,'system-message')]]"
    )

    last_visible = None
    for w in reversed(wrappers):
        if w.is_displayed():
            last_visible = w
            break

    if last_visible is None:
        raise RuntimeError("可視状態のメッセージが見つかりませんでした。")

    # 種別判定 & 本文・時刻の抽出
    if last_visible.find_elements(By.CSS_SELECTOR, ".system-message"):
        msg_type = "system"
    elif last_visible.find_elements(By.CSS_SELECTOR, ".user-message.you"):
        msg_type = "User"
    else:
        msg_type = "user"

    if msg_type == "user":
        # 本文 - 複数のセレクターを試行
        text = ""
        time_text = ""
        
        # 複数の可能なセレクターを試行
        selectors = [
            ".text-balloon",
            ".message-text",
            ".text-content", 
            ".message-content",
            ".user-message-text",
            ".balloon-text"
        ]
        
        body_el = None
        for selector in selectors:
            try:
                body_el = last_visible.find_element(By.CSS_SELECTOR, selector)
                text = body_el.text.strip()
                break
            except:
                continue
        
        # どのセレクターでも見つからない場合は、user-message内のテキストを直接取得
        if not text:
            try:
                user_msg_el = last_visible.find_element(By.CSS_SELECTOR, ".user-message")
                text = user_msg_el.text.strip()
            except:
                # 最後の手段として、last_visibleのテキスト全体を取得
                text = last_visible.text.strip()
        
        # 時刻（なければ空文字）
        time_els = last_visible.find_elements(By.CSS_SELECTOR, ".user-message-time")
        time_text = time_els[0].text.strip() if time_els else ""
    else:
        # system メッセージ - 複数のセレクターを試行
        text = ""
        time_text = ""
        
        # system メッセージ用の複数の可能なセレクターを試行
        system_selectors = [
            ".system-ballon",
            ".system-balloon", 
            ".system-message-text",
            ".system-content",
            ".message-text",
            ".text-content"
        ]
        
        body_el = None
        for selector in system_selectors:
            try:
                body_el = last_visible.find_element(By.CSS_SELECTOR, selector)
                text = body_el.text.strip()
                break
            except:
                continue
        
        # どのセレクターでも見つからない場合は、system-message内のテキストを直接取得
        if not text:
            try:
                system_msg_el = last_visible.find_element(By.CSS_SELECTOR, ".system-message")
                text = system_msg_el.text.strip()
            except:
                # 最後の手段として、last_visibleのテキスト全体を取得
                text = last_visible.text.strip()
        
        # system 側も先頭に「14:51」等が含まれることが多いので簡易抽出
        # 例: "14:51\n【フォローされました】..." → 1行目が時刻らしければ採用
        lines = text.splitlines()
        time_text = lines[0].strip() if lines and (":" in lines[0]) else ""

        
    return {
        "type": msg_type,      # "user" | "system"
        "time": time_text,     # "14:51" 等（取得できなければ ""）
        "text": text,          # 本文（リンクテキスト含む）
        "element": last_visible # 必要なら後続処理で使える WebElement
    }


