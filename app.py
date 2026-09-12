import os

from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


app = Flask(__name__)

# Giới hạn kích thước request
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB

# Cookie security
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# Rate limiting
#
# memory:// phù hợp cho instance đơn.
# Nếu chạy nhiều instance, hãy dùng Redis và đặt:
# RATELIMIT_STORAGE_URI=redis://...
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[
        "200 per minute",
        "1000 per hour",
    ],
    storage_uri=os.environ.get(
        "RATELIMIT_STORAGE_URI",
        "memory://",
    ),
)


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = (
        "strict-origin-when-cross-origin"
    )

    # Chỉ bật HSTS khi request thực sự chạy qua HTTPS.
    if request.is_secure:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

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


# Không cần app.run() trên Render.
# Render sẽ chạy:
# gunicorn app:app

