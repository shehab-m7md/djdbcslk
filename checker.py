import os
from bs4 import BeautifulSoup
from curl_cffi import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "9153292471:AAHyZ1Ia5uzwjsPYUMjF1708rujeUm6oWr8")
CHAT_IDS = ["7382848216"]

# بيانات جيت هب عشان يقفل نفسه بنفسه أول ما تلاقي الحفلة
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_NAME = os.environ.get("GITHUB_REPOSITORY")  # مثال: "username/repo-name"
WORKFLOW_FILE = "checker.yml"  # اسم ملف الـ yml بتاعك

LINKS = [
    "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza&m=avengers-doomsday",
    "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza&m=avengers-doomsday&d=20261217",
    "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza&m=avengers-doomsday&d=20261218",
    "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza&m=avengers-doomsday&d=20261219",
    "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza&m=avengers-doomsday&d=20261220",
    "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza&m=avengers-doomsday&d=20261221",
    "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza&m=avengers-doomsday&d=20261222",
    "https://egy.voxcinemas.com/showtimes?c=city-centre-almaza&m=avengers-doomsday&d=20261223",
    "https://egy.voxcinemas.com/showtimes?c=mall-of-egypt&m=avengers-doomsday",
    "https://egy.voxcinemas.com/showtimes?c=mall-of-egypt&m=avengers-doomsday&d=20261217",
    "https://egy.voxcinemas.com/showtimes?c=mall-of-egypt&m=avengers-doomsday&d=20261218",
    "https://egy.voxcinemas.com/showtimes?c=mall-of-egypt&m=avengers-doomsday&d=20261219",
    "https://egy.voxcinemas.com/showtimes?c=mall-of-egypt&m=avengers-doomsday&d=20261220",
    "https://egy.voxcinemas.com/showtimes?c=mall-of-egypt&m=avengers-doomsday&d=20261221",
    "https://egy.voxcinemas.com/showtimes?c=mall-of-egypt&m=avengers-doomsday&d=20261222",
    "https://egy.voxcinemas.com/showtimes?c=mall-of-egypt&m=avengers-doomsday&d=20261223",
]


def has_4dx(html):
    soup = BeautifulSoup(html, "html.parser")
    for strong in soup.select(".dates ol.showtimes > li > strong"):
        li = strong.parent
        if "4DX" in strong.get_text().upper() and li.select("a.showtime"):
            return True
    return False


def send_telegram(text):
    for chat_id in CHAT_IDS:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=30,
        )


def disable_github_workflow():
    if not GITHUB_TOKEN or not REPO_NAME:
        print("[!] بيانات جيت هب مش متوفرة عشان نقفل الأوتوميشن تلقائياً.")
        return
    
    try:
        # الأول نجيب الـ ID بتاع الـ Workflow
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        url_list = f"https://api.github.com/repos/{REPO_NAME}/actions/workflows"
        res = requests.get(url_list, headers=headers).json()
        
        workflow_id = None
        for wf in res.get("workflows", []):
            if wf["path"].endswith(WORKFLOW_FILE):
                workflow_id = wf["id"]
                break
                
        if workflow_id:
            # بعدين نعمله Disable
            url_disable = f"https://api.github.com/repos/{REPO_NAME}/actions/workflows/{workflow_id}/disable"
            requests.put(url_disable, headers=headers)
            print("[✓] تم إيقاف الأوتوميشن على جيت هب بنجاح عشان مايشتغلش تاني.")
    except Exception as e:
        print(f"[x] فشل إيقاف الأوتوميشن أوتوماتيك: {e}")


# التنفيذ الأساسي
found = False
for link in LINKS:
    try:
        r = requests.get(link, impersonate="chrome", timeout=30)
        if has_4dx(r.text):
            print(f"[✓] 4DX موجودة: {link}")
            send_telegram(f"🚨 4DX نزلت!\n{link}")
            found = True
            break  # بيوقف اللوب ومايكملش باقي اللينكات أول ما يلاقيه
        else:
            print(f"[-] مفيش 4DX: {link}")
    except Exception as e:
        print(f"[x] مقدرتش أفتح {link}: {e}")

# لو لقاها بيقفل الأوتوميشن خالص
if found:
    disable_github_workflow()
