import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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

    for i in range(config["shinsei_attempts"]):
        # 振込ページへ移動
        driver.execute_script("location.href='/SFC/apps/services/www/SFC/desktopbrowser/default/transfer/selectBeneficiary?mode=1';")
        time.sleep(5)  # 念の為5秒の待機時間を設ける

        # 登録済み振込先へ振込を選ぶ
        driver.execute_script("exeSubmitFormName('formRegtTransfer')")
        time.sleep(5)  # 念の為5秒の待機時間を設ける

        # 上から何番目の振込先かを指定し、次へ
        driver.execute_script(f"exeSubmitFormNameArg('formNext','registNo','{config['jibun_address_order']}');")
        time.sleep(5)  # 念の為5秒の待機時間を設ける

        # 振込金額の入力
        amount_input = driver.find_element(by=By.ID, value="piaAmt")
        amount_input.send_keys(config["jibun_amount"])

        # 「確認する」ボタンをクリック
        driver.find_element(by=By.CLASS_NAME, value="js-validate-submit").click()
        time.sleep(5)  # 念の為5秒の待機時間を設ける

        # 振り込み実行
        driver.execute_script("exeSubmitFormName('piaForm');")
        time.sleep(5)  # 念の為5秒の待機時間を設ける
        
        for i in range(240):
            result = driver.execute_script("return document.getElementsByClassName('c-hdg-level2')[0].innerText")
            if result == "振込受付完了":
                print("[+] 振り込み受付完了を確認しました。続行します。")
                break
            time.sleep(1)
        else:
            print("[-] 振り込み受付完了を確認できませんでした。10秒後に続行します。")
            time.sleep(10)  # 次の振込まで10秒待機

    return "done"
