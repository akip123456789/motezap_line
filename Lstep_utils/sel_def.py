from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta
import time
def get_data_sort_value(driver, date):
    try:
        # 日付に一致する行を待機しながら探す
        row = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, f"//th[normalize-space()='{date}']/ancestor::tr"))
        )
        
        # その行内で data-col="0" を持つ td 要素を待機しながら探す
        td_element = WebDriverWait(row, 120).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "td[data-col='0']"))
        )
        
        # td 要素から data-sort 属性値を取得
        return td_element.get_attribute("data-sort")
    except (NoSuchElementException, TimeoutException):
        print(f"指定した日付またはデータが見つかりませんでした: {date}")
        return None


def get_data_select_sort_value(driver, date,col):
    try:
        # 日付に一致する行を待機しながら探す
        row = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, f"//th[normalize-space()='{date}']/ancestor::tr"))
        )
        
        # その行内で data-col="0" を持つ td 要素を待機しながら探す
        td_element = WebDriverWait(row, 120).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"td[data-col='{col}']"))
        )
        
        # td 要素から data-sort 属性値を取得
        return td_element.get_attribute("data-sort")
    except (NoSuchElementException, TimeoutException):
        print(f"指定した日付またはデータが見つかりませんでした: {date}")
        return None

def click_link_with_attribute_and_text(driver, attribute, text):
    try:
        link_element = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@{attribute} and contains(text(), '{text}')]"))
        )
        link_element.click()
    except TimeoutException:
        print(f"指定した属性とテキストを持つリンクが見つかりませんでした: {text}")

def click_link_with_attribute_and_text1(driver, attribute, text):
    try:
        # XPathを使って属性と完全に一致するテキストを持つaタグを見つける
        link_element = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@{attribute}][text()='{text}']"))
        )
        link_element.click()
    except TimeoutException:
        print(f"指定した属性とテキストを持つリンクが見つかりませんでした: {text}")


def click_link_by_exact_text(driver, text):
    try:
        link_element = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[.='{text}']"))
        )
        link_element.click()
    except TimeoutException:
        print(f"完全に一致するテキストを持つリンクが見つかりませんでした: {text}")


def click_link_by_text(driver, text):
    try:
        link_element = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{text.strip()}')]"))
        )
        link_element.click()
    except TimeoutException:
        print(f"指定したテキストを持つリンクが見つかりませんでした: {text}")


def click_input_by_placeholder_text(driver, placeholder, text):
    try:
        input_element = WebDriverWait(driver, 180).until(
            EC.presence_of_element_located((By.XPATH, f"//input[@placeholder='{placeholder}']"))
        )        
        input_element.clear()  # 既存のテキストをクリア
        input_element.send_keys(text)  # 新しいテキストを入力
    except NoSuchElementException:
        print(f"要素が見つかりませんでした: {placeholder}")

def click_input_by_placeholder(driver, placeholder):
    try:
        input_element = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, f"//input[@placeholder='{placeholder}']"))
        )
        input_element.click()
    except TimeoutException:
        print(f"指定したplaceholderを持つ要素が見つかりませんでした: {placeholder}")


def id_click(driver,element_id):
    try: 
        button = WebDriverWait(driver, 300).until(
            EC.element_to_be_clickable((By.ID, element_id))
        )
        button.click()
    except NoSuchElementException:
        print(f"要素が見つかりませんでした: {element_id}")

def enter_text_in_input(driver, name, text):
    try:
        input_element = driver.find_element(By.NAME, name)
        input_element.clear()  # 既存のテキストをクリア
        input_element.send_keys(text)  # 新しいテキストを入力
    except NoSuchElementException:
        print(f"要素が見つかりませんでした: {name}")

def enter_text_in_id(driver, element_id, text):
    try:
        input_element = driver.find_element(By.ID, element_id)
        input_element.clear()  # 既存のテキストをクリア
        input_element.send_keys(text)  # 新しいテキストを入力
        return True
    except NoSuchElementException:
        print(f"要素が見つかりませんでした: {element_id}")
        return False
        
def enter_text_in_partial_id(driver, partial_id, text, timeout=10):
    try:
        # id属性に部分一致する要素を待機して取得
        xpath = f"//*[contains(@id, '{partial_id}')]"
        input_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        input_element.clear()
        input_element.send_keys(text + Keys.ENTER)
        return True
    except TimeoutException:
        print(f"タイムアウトしました。{timeout}秒以内に要素が見つかりませんでした: {partial_id}")
        return False
    except NoSuchElementException:
        print(f"部分一致するIDを持つ要素が見つかりませんでした: {partial_id}")
        return False
    

def class_click(driver, class_name):
    try: 
        button = WebDriverWait(driver, 180).until(
            EC.element_to_be_clickable((By.CLASS_NAME, class_name))
        )
        button.click()
    except NoSuchElementException:
        print(f"要素が見つかりませんでした: {class_name}")


def click_6th_element_with_class_partial(driver, partial_class,index,timeout=30):
    try:
        # すべての該当要素を取得（presence を待機）
        xpath = f"//*[contains(@class, '{partial_class}')]"
        WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath))
        )
        elements = driver.find_elements(By.XPATH, xpath)

        if len(elements) >= index:
            elements[index].click()  # 6番目（0-based index）
            return True
        else:
            print(f"{partial_class} を含む要素が 6 個未満しか見つかりませんでした（{len(elements)} 個）。")
            return False
    except TimeoutException:
        print(f"{timeout} 秒以内に要素が見つかりませんでした。")
        return False
def new_class_click(driver, class_name, element_name=None):
    try:
        # name 属性も使用して要素を特定
        if element_name:
            button = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.NAME, element_name))
            )
        else:
            button = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.CLASS_NAME, class_name))
            )
        button.click()
    except NoSuchElementException:
        print(f"要素が見つかりませんでした: {class_name}")
    except TimeoutException:
        print(f"クリック可能な要素が見つかりませんでした: {class_name}")


def class_click2(driver, class_name):
    try:
        # 指定されたクラス名を持つすべての要素をリストとして取得
        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, class_name))
        )
        # リストの2番目の要素（インデックス1）を取得
        if len(elements) > 1:
            second_element = elements[3]
            # 2番目の要素がクリック可能であればクリック
            if second_element.is_displayed() and second_element.is_enabled():
                second_element.click()
            else:
                # JavaScriptを使用してクリックを試みる
                driver.execute_script("arguments[0].click();", second_element)
        else:
            print(f"要素は1つしか見つかりませんでした: {class_name}")
    except NoSuchElementException:
        print(f"要素が見つかりませんでした: {class_name}")
    except TimeoutException:
        print(f"要素の検索中にタイムアウトしました: {class_name}")

def class_click_ss(driver, class_name,s):
    try:
        # 指定されたクラス名を持つすべての要素をリストとして取得
        elements = WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, class_name))
        )
        # リストの2番目の要素（インデックス1）を取得
        if len(elements) > s+1:
            second_element = elements[s]
            # 2番目の要素がクリック可能であればクリック
            if second_element.is_displayed() and second_element.is_enabled():
                try:
                    second_element.click()
                except:
                    driver.execute_script(f"arguments[s].click();", second_element)

            else:
                # JavaScriptを使用してクリックを試みる
                driver.execute_script(f"arguments[s].click();", second_element)
        else:
            print(f"要素は1つしか見つかりませんでした: {class_name}")
    except NoSuchElementException:
        print(f"要素が見つかりませんでした: {class_name}")
    except TimeoutException:
        print(f"要素の検索中にタイムアウトしました: {class_name}")




def class_input_ss(driver, class_name,text,index):
    try:
        # 指定されたクラス名を持つすべての要素をリストとして取得
        elements = WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, class_name))
        )

        # 指定されたインデックスの要素にテキストを入力
        if len(elements) > index:
            target_element = elements[index]
            if target_element.is_displayed() and target_element.is_enabled():
                target_element.send_keys(text)
            else:
                # 要素が表示されていないか、入力不可能な場合
                print("要素が表示されていないか、入力不可能です。")
        else:
            # 指定されたインデックスの要素が存在しない場合
            print(f"要素が存在しません。指定されたインデックス: {index}, 要素の総数: {len(elements)}")
    except NoSuchElementException:
        print(f"要素が見つかりませんでした: {class_name}")
    except TimeoutException:
        print(f"要素の検索中にタイムアウトしました: {class_name}")






def class_input_ss_d(driver, class_name,text,index):
    try:
        # 指定されたクラス名を持つすべての要素をリストとして取得
        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, class_name))
        )

        # 指定されたインデックスの要素にテキストを入力
        if len(elements) > index:
            target_element = elements[index]
            if target_element.is_displayed() and target_element.is_enabled():
                for i in range(15):
                    target_element.send_keys(Keys.BACKSPACE)

                target_element.send_keys(text)
            else:
                # 要素が表示されていないか、入力不可能な場合
                print("要素が表示されていないか、入力不可能です。")
        else:
            # 指定されたインデックスの要素が存在しない場合
            print(f"要素が存在しません。指定されたインデックス: {index}, 要素の総数: {len(elements)}")
    except NoSuchElementException:
        print(f"要素が見つかりませんでした: {class_name}")
    except TimeoutException:
        print(f"要素の検索中にタイムアウトしました: {class_name}")


def input_click(driver, name):
    try:
        input_element = driver.find_element(By.NAME, name)
        input_element.click()
    except NoSuchElementException:
        print(f"要素が見つかりませんでした: {name}")


def input_click(driver, name):
    try: 
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, name))
        )
        button.click()
    except NoSuchElementException:
        print(f"要素が見つかりませんでした: {name}")

def inout_value_click(driver,value):
    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//input[@value='{value}']"))
        )
        submit_button.click()
    except TimeoutException:
        print("指定したvalueを持つ要素が見つかりませんでした。")

def click_div_by_text(driver, text):
    try:
        div_element = WebDriverWait(driver, 100).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{text}')]"))
        )
        try:
            div_element.click()
        except:
            driver.execute_script("arguments[0].click();", div_element)
    except TimeoutException:
        print(f"指定したテキストを持つ要素が見つかりませんでした: {text}")

def click_span_by_text(driver, text):
    try:
        span_element = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[contains(., '{text}')]"))
        )
        span_element.click()
    except TimeoutException:
        print(f"指定したテキストを持つ要素が見つかりませんでした: {text}")

def click_link_by_text(driver, text):
    try:
        link_element = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{text}')]"))
        )
        link_element.click()
    except TimeoutException:
        print(f"指定したテキストを持つリンクが見つかりませんでした: {text}")


def click_span_by_text123(driver, text):
    try:
        # 指定されたテキストを持つspan要素を探してクリック
        span_element = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[@class='btn liny-button primary' and normalize-space()='{text}']"))
        )
        span_element.click()
    except TimeoutException:
        print(f"指定したテキストを持つ要素が見つかりませんでした: {text}")


def select_option_by_text(driver, select_xpath, option_text):
    try:
        select_element = Select(driver.find_element(By.XPATH, select_xpath))
        select_element.select_by_visible_text(option_text.strip())
    except NoSuchElementException:
        print(f"指定したテキストを持つoption要素が見つかりませんでした: {option_text}")


def get_data_sort_value2(driver, data_col_value, timeout=300):
    try:
        # 要素が見つかるまで待機
        td_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, f"//td[@data-col='{data_col_value}']"))
        )
        # td要素からdata-sort属性の値を取得
        return td_element.get_attribute("data-sort")
    except TimeoutException:
        print(f"タイムアウト: data-col='{data_col_value}' を持つ要素が見つかりませんでした。")
        return False
    except NoSuchElementException:
        print(f"data-col='{data_col_value}' を持つ要素が見つかりませんでした。")
        return False
    
def day_set1(driver,number):
    try:
        # 指定されたテキストを持つすべてのspan要素を取得
        elements = WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.XPATH, f"//span[contains(@class, 'cell day') and text()='{number}']"))
        )
        # 要素が2つ以上ある場合、2番目の要素をクリック
        if len(elements) > 1:
            second_element = elements[0]
            try:
                time.sleep(5)
                second_element.click()
                print("second_elementを正常にクリック1")
            except:
                driver.execute_script("arguments[0].click();", second_element)
                print("second_elementを正常にクリックできませんでした")
        else:
            print(f"指定したテキスト'{number}'を持つ要素は1つしか見つかりませんでした。")
            second_element = elements[0]
            try:
                time.sleep(5)
                second_element.click()
                print("second_elementを正常にクリック2")
            except:
                driver.execute_script("arguments[0].click();", second_element)
                print("second_elementを正常にクリックできませんでした")
    except TimeoutException:
        print(f"指定したテキスト'{number}'を持つ要素の検索中にタイムアウトしました。")


def day_set2(driver, number):
    try:
        # 指定されたテキストを持つすべてのspan要素を取得
        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, f"//span[contains(@class, 'cell day') and text()='{number}']"))
        )

        # 要素が1つ以上ある場合、2番目の要素をクリック
        if len(elements) > 1:
            second_element = elements[1]
            try:
                time.sleep(5)
                second_element.click()
            except:
                driver.execute_script("arguments[0].click();", second_element)
        else:
            print(f"指定したテキスト'{number}'を持つ要素は1つしか見つかりませんでした。")
            second_element = elements[0]
            try:
                time.sleep(5)
                second_element.click()
                print("second_elementを正常にクリック")
            except:
                driver.execute_script("arguments[0].click();", second_element)
                print("second_elementを正常にクリックできませんでした")

    except TimeoutException:
        print(f"指定したテキスト'{number}'を持つ要素の検索中にタイムアウトしました。")

def get_class(driver, class_name):
    try:
        # 指定されたクラスを持つspan要素を探す
        span_element = WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )        
        return span_element.text
    except NoSuchElementException:
        print(f"指定したクラスを持つ要素が見つかりませんでした: {class_name}")
        return None
    
def get_class2(driver, class_name):
    try:
        # 指定されたクラスを持つ全てのspan要素を探す
        elements = WebDriverWait(driver, 300).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, class_name))
        )        
        # リストに少なくとも2つの要素があるか確認
        if len(elements) >= 2:
            return elements[2].text  # 2番目の要素のテキストを返す
        else:
            print(f"指定したクラスを持つ要素が2つありません: {class_name}")
            return None
    except NoSuchElementException:
        print(f"指定したクラスを持つ要素が見つかりませんでした: {class_name}")
        return None
    

def get_class_ss(driver,class_name,s):
    try:
        # 指定されたクラスを持つ全てのspan要素を探す
        elements = WebDriverWait(driver, 300).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, class_name))
        )      

        # リストに少なくとも2つの要素があるか確認
        if len(elements) >= s+1:
            return elements[s].text  # 2番目の要素のテキストを返す
        else:
            print(f"指定したクラスを持つ要素が2つありません: {class_name}")
            return None
    except NoSuchElementException:
        print(f"指定したクラスを持つ要素が見つかりませんでした: {class_name}")
        return None
    


def td_click(driver, text):
    try:
        element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, f"//td[contains(normalize-space(), '{text}')]"))
        )
        # 要素をクリック
        element.click()
    except Exception as e:
        print("要素が見つからないか、クリックできませんでした。", e)



def td_click_or(driver, text,or_exact_match):
    # 完全一致ではない
    if or_exact_match=="no_exact_match":
        try:
            element = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, f"//td[contains(normalize-space(), '{text}')]"))
            )
            # 要素をクリック
            element.click()
        except Exception as e:
            print("要素が見つからないか、クリックできませんでした。", e)
    # 完全一致
    if or_exact_match=="exact_match":
        try:
            element = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, f"//td[normalize-space(text())='{text}']"))
            )
            # 要素をクリック
            element.click()
        except Exception as e:
            print("要素が見つからないか、クリックできませんでした。", e)

def get_text_from_td(driver, td_number):
    try:        # ページ内のすべてのtdタグを取得
        td_elements = driver.find_elements(By.TAG_NAME, 'td')
        # 指定された番号のtdタグのテキストを返す
        return td_elements[td_number].text
    except IndexError:
        return "指定された番号のtdタグは存在しません。"
    except NoSuchElementException:
        return "tdタグが見つかりません。"
    

def click_and_scroll_on_div(driver, text):
    try:
        # 指定したテキストを含むdiv要素をクリック可能になるまで待機
        div_element = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{text}')]"))
        )
        # 要素をクリック
        div_element.click()

        # ActionChainsを使用して要素にスクロール
        actions = ActionChains(driver)
        actions.move_to_element(div_element).perform()  # 要素にポインタを移動
        actions.scroll(0, 800).perform()  # 例えば100ピクセル下にスクロール

    except TimeoutException:
        print(f"指定したテキストを持つ要素が見つかりませんでした: {text}")



def sheet_month(driver, month):
    try:
        # 月の完全なテキストが一致する要素を待ちます
        element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, f"//span[. = '{month}']"))
        )
        # 通常のクリックを試みます
        try:
            element.click()
        except Exception as e:
            print("通常のクリックに失敗しました。JavaScriptでクリックを試みます。エラー:", e)
            driver.execute_script("arguments[0].click();", element)
    except Exception as e:
        print("エラーが発生しました:", e)
