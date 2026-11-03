# 課間｜Django 個人課表系統（登入版）

三頁：個人課表、選課資訊、專注計時。新增登入、註冊、POST 登出，使用 Django 內建帳號與密碼雜湊。每個帳號分別保存課表；同一伺服器同一帳號可在不同瀏覽器登入存取。沒有預設帳密，第一次先註冊。

## Windows

安裝 Python 3.10 以上，完整解壓縮後雙擊 run_windows.bat。首次需網路安裝套件。看到 Starting development server 後開啟 http://127.0.0.1:8000/ ，會進入登入頁。點建立帳號註冊後使用。保持命令視窗開啟。

## macOS / Linux

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 更新舊 Django 專案

先備份舊資料夾（包含 db.sqlite3 與 .dev-secret），關閉伺服器後覆蓋新版程式，保留原 db.sqlite3、.dev-secret 與 .venv。重新執行 run_windows.bat，會自動套用新增的資料庫 migration。

使用原瀏覽器開啟相同網址註冊／登入時，如果帳號尚無課表，會把這個瀏覽器原本的匿名課表歸到該帳號。帳號若已有課表，優先保留帳號資料；舊資料仍在資料庫。最穩妥方式是更新前先匯出 JSON，登入新版後再匯入。

## GitHub

上傳 config、pages、manage.py、requirements.txt、pyproject.toml、README.md 與三個 bat 檔，保留資料夾結構。不要上傳 .venv、db.sqlite3、.dev-secret、__pycache__。此為 Django 本機版本，GitHub Pages 無法執行後端；原靜態展示網址不會因此更新。

## 測試

python manage.py check
python manage.py test pages

密碼遺忘可由專案管理者用 python manage.py changepassword 帳號 重設。本版不含電子郵件驗證或寄信重設密碼。計時設定仍保存在瀏覽器，課表存在伺服器 SQLite。不同電腦各自啟動的本機伺服器不共用資料。
