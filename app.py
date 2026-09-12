from datetime import datetime
import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1548284221213245481/5_62xA-rvF8mIpnr__dwKChr6M-uz59LovQVl-xV1JzJlPJKVfo1MqBmncj7oGnYjvru"


def send_discord_alert(ip, user_agent, path):
  try:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "content": "🚨 **[CẢNH BÁO] Có người truy cập hệ thống!**",
        "embeds": [{
            "title": "Chi tiết lượt truy cập",
            "color": 16711680,
            "fields": [
                {"name": "🌐 Địa chỉ IP", "value": f"`{ip}`", "inline": True},
                {"name": "📂 Đường dẫn", "value": f"`{path}`", "inline": True},
                {"name": "⏰ Thời gian", "value": f"`{now}`", "inline": False},
                {
                    "name": "💻 Thiết bị / Trình duyệt",
                    "value": f"```{user_agent}```",
                    "inline": False,
                },
            ],
        }],
    }

    # Thêm timeout=3 để tránh bị treo app nếu Discord phản hồi chậm
    response = requests.post(
        DISCORD_WEBHOOK_URL, json=payload, timeout=3
    )
    print(f"Discord Response Status: {response.status_code}")  # In ra log Render
  except Exception as e:
    print(f"LỖI GỬI WEBHOOK: {e}")  # In lỗi chi tiết ra log Render


@app.route("/")
def home():
  if request.headers.get("X-Forwarded-For"):
    ip = request.headers.get("X-Forwarded-For").split(",")[0].strip()
  else:
    ip = request.remote_addr

  user_agent = request.headers.get("User-Agent", "Unknown")
  path = request.path

  # Kích hoạt gửi thông báo
  send_discord_alert(ip, user_agent, path)

  return render_template("index.html")


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
