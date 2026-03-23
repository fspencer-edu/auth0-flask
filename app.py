import os
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, session, url_for
from authlib.integrations.flask_client import OAuth

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("APP_SECRET_KEY")
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")

oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f"https://{AUTH0_DOMAIN}/.well-known/openid-configuration",
)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return render_template("home.html", user=session.get("user"))

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback")
def callback():
    token = oauth.auth0.authorize_access_token()
    user = token.get("userinfo") or oauth.auth0.userinfo()
    session["user"] = user
    return redirect(url_for("profile"))

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=session["user"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        f"https://{AUTH0_DOMAIN}/v2/logout"
        f"?client_id={AUTH0_CLIENT_ID}"
        f"&returnTo={url_for('home', _external=True)}"
    )

if __name__ == "__main__":
    app.run(debug=True, port=5173)