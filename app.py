from datetime import datetime
import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Discord Webhook URL của bạn
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1548284221213245481/5_62xA-rvF8mIpnr__dwKChr6M-uz59LovQVl-xV1JzJlPJKVfo1MqBmncj7oGnYjvru"


def send_discord_alert(ip, user_agent, path):
  try:
    # Lấy thời gian hiện tại
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Tạo nội dung tin nhắn đẹp mắt trên Discord (dùng Embed hoặc text thường)
    payload = {
        "content": "🚨 **[CẢNH BÁO] Có người truy cập vào hệ thống!**",
        "embeds": [{
            "title": "Thông tin chi tiết lượt truy cập",
            "color": 16711680,  # Màu đỏ cảnh báo
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

    # Gửi request tới Discord
    requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
  except Exception as e:
    print(f"Lỗi khi gửi webhook Discord: {e}")


@app.route("/")
def home():
  # Lấy IP thực của người truy cập (xử lý trường hợp chạy sau Proxy/Cloudflare/Render)
  if request.headers.get("X-Forwarded-For"):
    ip = request.headers.get("X-Forwarded-For").split(",")[0].strip()
  else:
    ip = request.remote_addr

  user_agent = request.headers.get("User-Agent")
  path = request.path

  # Gửi thông báo ngầm sang Discord (không làm chậm tốc độ tải trang của người dùng)
  send_discord_alert(ip, user_agent, path)

  return render_template("index.html")


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
