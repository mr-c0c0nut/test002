from datetime import datetime
import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1548284221213245481/5_62xA-rvF8mIpnr__dwKChr6M-uz59LovQVl-xV1JzJlPJKVfo1MqBmncj7oGnYjvru"


def send_discord_alert(ip, user_agent, path):
  try:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = (
        f"🚨 **CÓ NGƯỜI TRUY CẬP WEB!**\n"
        f"🌐 **IP:** `{ip}`\n"
        f"📂 **Đường dẫn:** `{path}`\n"
        f"⏰ **Thời gian:** `{now}`\n"
        f"💻 **Thiết bị:** ```{user_agent}```"
    )
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    print(f"Trạng thái gửi Discord: {response.status_code}")
  except Exception as e:
    print(f"Lỗi ngoại lệ khi gửi webhook: {e}")


@app.route("/")
def home():
  user_agent = request.headers.get("User-Agent", "")

  # BỎ QUA nếu request đến từ bot health check của Render (tránh lỗi 429)
  if "Go-http-client" in user_agent:
    return render_template("index.html")

  if request.headers.get("X-Forwarded-For"):
    ip = request.headers.get("X-Forwarded-For").split(",")[0].strip()
  else:
    ip = request.remote_addr

  path = request.path

  # Gửi thông báo khi có người dùng thật truy cập
  send_discord_alert(ip, user_agent, path)

  return render_template("index.html")


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
