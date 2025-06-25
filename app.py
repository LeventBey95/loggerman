from flask import Flask, request, render_template
from datetime import datetime
import requests
import user_agents
import os
import json

app = Flask(__name__)

JSON_LOG_PATH = 'logs.json'  # logs.json dosyasına kayıt yapılacak

def get_geo_info(ip_address):
    try:
        response = requests.get(f"https://ipinfo.io/{ip_address}/json")
        if response.status_code == 200:
            data = response.json()
            return {
                "city": data.get("city", "Bilinmiyor"),
                "region": data.get("region", "Bilinmiyor"),
                "country": data.get("country", "Bilinmiyor"),
                "location": data.get("loc", "Bilinmiyor")
            }
    except:
        pass
    return {
        "city": "Bilinmiyor",
        "region": "Bilinmiyor",
        "country": "Bilinmiyor",
        "location": "Bilinmiyor"
    }

def append_json_log(data):
    logs = []
    if os.path.exists(JSON_LOG_PATH):
        with open(JSON_LOG_PATH, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except Exception:
                logs = []
    logs.append(data)
    with open(JSON_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

@app.route('/')
def ziyaretci_bilgisi():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')
    parsed_ua = user_agents.parse(user_agent)
    geo = get_geo_info(ip)
    result = {
        "timestamp": datetime.now().isoformat(),
        "ip": ip,
        "city": geo['city'],
        "region": geo['region'],
        "country": geo['country'],
        "location": geo['location'],
        "device": parsed_ua.device.family,
        "os": f"{parsed_ua.os.family} {parsed_ua.os.version_string}",
        "browser": f"{parsed_ua.browser.family} {parsed_ua.browser.version_string}",
        "user_agent": user_agent
    }
    append_json_log(result)
    return render_template("welcome.html")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)