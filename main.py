import selenium.common.exceptions
import yaml
import os
import undetected_chromedriver as uc
from core.jibunbank import jibunbank


def load_config() -> dict:
    with open("./config.yaml", "r", encoding="utf-8") as f:
        try:
            config_file = yaml.safe_load(f)    
        except FileNotFoundError:
            raise FileNotFoundError("[-] config.yamlが設置されていません。")
    try:
        config = {
            "jibun_customer_no": config_file["jibun_customer_no"],
            "jibun_password": config_file["jibun_password"],
            "jibun_attempts": config_file["jibun_attempts"],
            "jibun_address_order": config_file["jibun_address_order"],
            "jibun_amount": config_file["jibun_amount"],
            "chrome_path": config_file["chrome_path"]
        }
        return config
    except KeyError as e:
        raise ValueError(f"[-] 構成が正しくありません。キーエラーです: {e}")


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


if __name__ == "__main__":
    config = load_config()

    info = """
==================================================
    ポイ活自動化ツール by Mutsuki

    Github:
    https://github.com/mutsukitan/poikatsu

    Twitter(現: X):
    https://twitter.com/mutsukitan
==================================================

    1: auじぶん銀行連続振込
    2: SBI新生銀行連続振込(近日対応予定)
    9: このツールについて
    0: exit
"""
    print(info)
    input_ = input("[?] オプションを選択してください: ")

    if input_ == "1":
        driver = open_browser()
        result = jibunbank(driver, config)
        if result == "done":
            driver.quit()
            print("[+] Process completed successfully.")
            print(info)

    elif input_ == "2":
        print("[-] 現在SBI新生銀行の自動振込には対応していません。")

    elif input_ == "9":
        about = "このツールはMutsukiによって作成されました。\n" \
        "トップメニューに記載のGithubリポジトリにて公開されています。\n" \
        "バグ報告や機能要望などがありましたら、GithubのIssueまでご連絡ください。"
    
    elif input_ == "0":
        print("[+] Exiting...")
        exit(0)