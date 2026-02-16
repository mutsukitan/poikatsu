import yaml
import os
import undetected_chromedriver as uc
import selenium.common.exceptions
from core.jibunbank import jibunbank
from core.shinsei import shinsei


def load_config() -> dict:
    with open("./config.yaml", "r", encoding="utf-8") as f:
        try:
            config_file = yaml.safe_load(f)    
        except FileNotFoundError:
            raise FileNotFoundError("[-] config.yamlが設置されていません。")
    try:
        config = {
            "jibun_customer_no": str(config_file["jibun_customer_no"]),
            "jibun_password": str(config_file["jibun_password"]),
            "jibun_attempts": int(config_file["jibun_attempts"]),
            "jibun_address_order": str(config_file["jibun_address_order"]),
            "jibun_amount": str(config_file["jibun_amount"]),

            "shinsei_customer_no": str(config_file["shinsei_customer_no"]),
            "shinsei_password": str(config_file["shinsei_password"]),
            "shinsei_attempts": int(config_file["shinsei_attempts"]),
            "shinsei_address_order": int(config_file["shinsei_address_order"]),
            "shinsei_amount": str(config_file["shinsei_amount"]),
            
            "chrome_path": str(config_file["chrome_path"])
        }
        return config
    except KeyError as e:
        raise ValueError(f"[-] 構成が正しくありません。キーエラーです: {e}")
    except ValueError as e:
        raise ValueError(f"[-] 構成の値の型が正しくありません。値エラーです: {e}")

def open_browser() -> uc.Chrome:
    profile_path = os.path.dirname(__file__) + "/chrome_profile"

    options = uc.ChromeOptions()

    options.user_data_dir = profile_path
    options.add_argument("--no-sandbox")
    options.add_argument('--start-maximized')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-web-security")
    options.add_argument("--enable-blink-features=TrustedDOMTypes")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    try:
        driver = uc.Chrome(
            headless=False,
            options=options,
            browser_executable_path=config["chrome_path"],
            user_data_dir=profile_path
        )
    except selenium.common.exceptions.SessionNotCreatedException:
        raise RuntimeError("[-] Chromeセッションを初期化できませんでした。Chromeのバージョンとundetected-chromedriverの互換性を確認してください。")
    except Exception as e:
        raise RuntimeError(f"[-] Chromeの起動中にエラーが発生しました: {e}")

    return driver

def main_prompt() -> bool:
    info = """
==================================================
    ポイ活自動化ツール by Mutsuki

    Github:
    https://github.com/mutsukitan/poikatsu

    Twitter(現: X):
    https://twitter.com/mutsukitan
==================================================

    1: auじぶん銀行連続振込
    2: SBI新生銀行連続振込
    9: このツールについて
    0: exit
"""
    print(info)
    input_ = input("[?] オプションを選択してください: ")

    if input_ == "1":
        print("[!] auじぶん銀行の連続振込を開始します。振り込み失敗を検知した場合10秒の待機時間があるため、その間に処理をキャンセルできます。")
        input("[+] Enterを押すと続行します。")
        driver = open_browser()
        result = jibunbank(driver, config)
        if result == "done":
            driver.quit()
            print("[+] auじぶん銀行連続振込が完了しました。")
        else:
            print("[-] auじぶん銀行連続振込が完了しませんでした。")
        return True

    elif input_ == "2":
        print("[!] SBI新生銀行の連続振込を開始します。振り込み失敗を検知した場合10秒の待機時間があるため、その間に処理をキャンセルできます。")
        input("[+] Enterを押すと続行します。")
        driver = open_browser()
        result = shinsei(driver, config)
        if result == "done":
            driver.quit()
            print("[+] SBI新生銀行連続振込が完了しました。")

        else:
            print("[-] SBI新生銀行連続振込が完了しませんでした。")
        return True

    elif input_ == "9":
        about = "このツールはMutsukiによって作成されました。\n" \
        "トップメニューに記載のGithubリポジトリにて公開されています。\n" \
        "バグ報告や機能要望などがありましたら、GithubのIssueまでご連絡ください。"
        print(about)
        return True
    
    elif input_ == "0":
        print("[!] Exiting...")
        return False
    
    else:
        print("[-] 無効なオプションです。もう一度選択してください。")
        return True


if __name__ == "__main__":
    config = load_config()

    while main_prompt():
        pass