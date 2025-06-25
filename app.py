from flask import Flask, request, render_template
from datetime import datetime
import requests
import user_agents
import os
import sqlite3

app = Flask(__name__)

DB_PATH = 'visitors.db'  # SQLite veritabanı dosyası

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ip TEXT,
            city TEXT,
            region TEXT,
            country TEXT,
            location TEXT,
            device TEXT,
            os TEXT,
            browser TEXT,
            user_agent TEXT
        )
    ''')
    conn.commit()
    conn.close()

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

def insert_visitor(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO visitors (
            timestamp, ip, city, region, country, location, device, os, browser, user_agent
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data["timestamp"],
        data["ip"],
        data["city"],
        data["region"],
        data["country"],
        data["location"],
        data["device"],
        data["os"],
        data["browser"],
        data["user_agent"]
    ))
    conn.commit()
    conn.close()

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
    insert_visitor(result)
    return render_template("welcome.html")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, use_reloader=False)