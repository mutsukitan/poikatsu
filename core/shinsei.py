import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from colorama import Fore


def shinsei(driver: uc.Chrome, config: dict) -> str:
    # ログインページへ
    driver.get("https://bk.web.sbishinseibank.co.jp/SFC/apps/services/www/SFC/desktopbrowser/default/login?mode=1")
    
    # 各種情報の入力
    customer_no = driver.find_element(by=By.NAME, value="nationalId")
    customer_no.send_keys(config["shinsei_customer_no"])

    password = driver.find_element(by=By.ID, value="loginPassword")
    password.send_keys(config["shinsei_password"])

    login_button = driver.find_element(by=By.CSS_SELECTOR, value="button.ng-scope")
    login_button.click()

    # ログイン完了まで待機（二段階認証などがある可能性）
    WebDriverWait(driver, 240, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "totalAmount")))

    # 振込ページへ移動
    transfer_page_button = driver.find_elements(by=By.CLASS_NAME, value="nav-link")  # ヘッダー部分の振込ボタン
    transfer_page_button[1].click()
    time.sleep(5)  # 念の為5秒の待機時間を設ける

    for i in range(config["shinsei_attempts"]):
        # 振込を行う→振込
        driver.find_element(by=By.CSS_SELECTOR, value='a[ng-click*="TR0002"]').click()
        time.sleep(5)  # 念の為5秒の待機時間を設ける

        # 上から何番目の振込先かを指定し、次へ
        transfer_list = driver.find_elements(by=By.CSS_SELECTOR, value='button[ng-click^="transfer("]')
        transfer_list[config["shinsei_address_order"]].click()
        time.sleep(5)  # 念の為5秒の待機時間を設ける

        # 振込金額の入力
        amount_input = driver.find_element(by=By.CSS_SELECTOR, value='input[ng-model="amount"]')
        amount_input.send_keys(config["shinsei_amount"])

        # 「次へ」をクリック
        driver.find_element(by=By.CSS_SELECTOR, value='button[ng-click^="next("]').click()
        time.sleep(5)  # 念の為5秒の待機時間を設ける

        # 認証画面へ
        # 電話認証が設定されてる場合は「実行（電話認証）」
        driver.find_element(by=By.CLASS_NAME, value="spAuth").click()

        # OTPの入力と振り込み受付完了を待機
        try:
            WebDriverWait(driver, 240, 1).until(EC.presence_of_element_located((By.ID, "label_transferComplete")))
        except TimeoutException:
            print(f"{Fore.RED}[-]{Fore.RESET} 振り込み受付完了を確認できませんでした。残り振込試行回数は{config['shinsei_attempts'] - i - 1}回です。10秒後に続行します。")
            time.sleep(10)  # 次の振込まで10秒待機
            continue
        
        print(f"{Fore.GREEN}[+]{Fore.RESET} 振り込み受付完了を確認しました。残り振込試行回数は{config['shinsei_attempts'] - i - 1}回です。続行します。")
        
        driver.find_element(by=By.CLASS_NAME, value="TR0009PrintAndNextBtn").click()

    return "done"
