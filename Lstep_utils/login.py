import time
import random
from selenium import webdriver
import os
import tempfile
from dotenv import load_dotenv
from os.path import join, dirname
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from twocaptcha import TwoCaptcha
from twocaptcha.api import NetworkException
import Lstep_utils.sel_def as sf
import os
load_dotenv()

TwoCaptcha_API=os.environ.get("TwoCaptcha_API")

solver = TwoCaptcha(TwoCaptcha_API)  # 自分のAPIキーを設定してください
url = 'https://recaptcha-demo.appspot.com/recaptcha-v2-checkbox.php'


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

def solve_recaptcha(data_sitekey, solver, url, max_retries=3, delay=5):
    """
    2CaptchaでreCAPTCHAを解く。ネットワークエラーが発生した場合、指定回数リトライする。
    :param data_sitekey: reCAPTCHAのサイトキー
    :param solver: TwoCaptchaのsolverオブジェクト
    :param url: 対象のURL
    :param max_retries: リトライ回数
    :param delay: リトライ前の待機秒数
    :return: 取得したcode文字列
    :raises Exception: リトライしても解決できなかった場合に例外を送出
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = solver.recaptcha(sitekey=data_sitekey, url=url)
            return response['code']
        except NetworkException as e:
            print(f"NetworkExceptionが発生しました (attempt={attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                print(f"{delay}秒待機して再度試します...")
                time.sleep(delay)
            else:
                # 最大リトライ回数を超えた場合は例外を送出
                raise Exception("2Captchaリクエストがすべて失敗しました") from e

def login():
    """
    ログインフローを実行。reCAPTCHAを2Captchaで解く。
    :param url: ログインURL
    :return: ログイン後のWebDriverインスタンス
    """
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_argument("--headless=new")
    options.add_argument('--disable-dev-shm-usage')
    unique_dir = tempfile.mkdtemp()
    options.add_argument(f'--user-data-dir={unique_dir}')
    
    # WebDriverの初期化
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1980,1080)
    driver.execute_script("""delete Object.getPrototypeOf(navigator).webdriver;""")

    # ログインページにアクセス
    url="https://manager.linestep.net/account/login"
    driver.get(url)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # 環境変数からユーザー名/パスワードを取得し、入力
    name_text = os.environ.get("LSETP_USERNAME")
    sf.input_click(driver, "name")
    sf.enter_text_in_input(driver, "name", name_text)

    password_text = os.environ.get("LSETP_PASSWORD")
    sf.input_click(driver, "password")
    sf.enter_text_in_input(driver, "password", password_text)

    # reCAPTCHAのiframeを待機してから切り替え
    try:
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[src*='recaptcha']"))
        )
    except TimeoutException:
        print("iframeのロードに時間がかかりすぎます。")
    
    # 一度デフォルトコンテキストへ戻しておく
    driver.switch_to.default_content()

    # デモ用のサイトキーをセット（実際には該当サイトに合わせて設定）
    data_sitekey = "6LcxKEIUAAAAAIcFpQk1amacsiZUfdKESVzBmZvN"
    print("[data-sitekey]----------------------------------------")
    print(data_sitekey)
    
    # 2Captchaで解除コードを取得（リトライロジック付き）
    code = solve_recaptcha(data_sitekey, solver, url)

    print("response code---------------------------------------")
    print(code)

    # reCAPTCHAレスポンスを埋め込みフォーム送信
    recaptcha_response_element = driver.find_element(By.ID, 'g-recaptcha-response')
    driver.execute_script(f'arguments[0].value = "{code}";', recaptcha_response_element)
    driver.execute_script('document.forms[0].submit()')

    time.sleep(random.uniform(1, 2))
    return driver


def account_select(driver,account_id):
    try:
        driver.get(f"https://manager.linestep.net/account?q=%40{account_id}")
        button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="メイン画面を開く"]'))
        )
        button.click()
    except Exception as e:
        print("クリックエラー:", e)