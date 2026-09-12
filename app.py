import os
from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)

# Không cho phép request body quá lớn
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB

# Cookie security
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,       # HTTPS
    SESSION_COOKIE_SAMESITE="Lax",
)

# Chỉ dùng ProxyFix nếu ứng dụng thực sự nằm sau reverse proxy
# và proxy của bạn được cấu hình để ghi header đúng cách.
if os.environ.get("TRUST_PROXY") == "1":
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
    )


# Rate limit theo địa chỉ mà Flask nhận được.
# Production nên dùng Redis thay cho memory storage.
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[
        "200 per minute",
        "1000 per hour",
    ],
    storage_uri=os.environ.get(
        "RATELIMIT_STORAGE_URI",
        "memory://"
    ),
)


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Chỉ bật HSTS khi website thực sự chạy HTTPS.
    if request.is_secure:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    # CSP cơ bản; điều chỉnh nếu index.html dùng CDN/script ngoài.
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none';"
    )

    return response


@app.route("/", methods=["GET"])
@limiter.limit("30 per minute")
def home():
    return render_template("index.html")


@app.errorhandler(413)
def request_too_large(error):
    return "Request too large", 413


@app.errorhandler(429)
def rate_limited(error):
    return "Too many requests. Please try again later.", 429


@app.errorhandler(500)
def internal_error(error):
    return "Internal server error", 500


if __name__ == "__main__":
    # Chỉ dùng cho development.
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="127.0.0.1",
        port=port,
        debug=False,
    )
