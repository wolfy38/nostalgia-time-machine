import os
import secrets
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import json
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from functools import wraps
import time
from bson.objectid import ObjectId


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "../templates")
STATIC_DIR = os.path.join(BASE_DIR, "../static")

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))


try:
    client = MongoClient("mongodb://localhost:27017/",
                         serverSelectionTimeoutMS=5000)
    client.server_info()
    db = client.nostalgia_db
    print("Successfully connected to MongoDB")
except ConnectionFailure as e:
    print(f"Could not connect to MongoDB: {e}")
    db = None
except Exception as e:
    print(f"Unexpected error connecting to MongoDB: {e}")
    db = None


app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(BASE_DIR, 'sessions')
app.config['SESSION_PERMANENT'] = False
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
try:
    os.chmod(app.config['SESSION_FILE_DIR'], 0o777)
except Exception as e:
    print(f"Error setting session directory permissions: {e}")
Session(app)

RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW = 60
user_requests = {}


def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Not logged in"}), 401
        user_id = session["user_id"]
        current_time = time.time()

        if user_id in user_requests:
            user_requests[user_id] = [
                t for t in user_requests[user_id] if current_time - t < RATE_LIMIT_WINDOW]
        else:
            user_requests[user_id] = []

        if len(user_requests[user_id]) >= RATE_LIMIT_REQUESTS:
            return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429

        user_requests[user_id].append(current_time)
        return f(*args, **kwargs)
    return decorated_function


def scrape_page(url):
    try:
        with urlopen(url, timeout=10) as response:
            soup = BeautifulSoup(response.read(), 'html.parser')
            return soup
    except (HTTPError, URLError) as e:
        print(f"Error scraping {url}: {e}")
        return None


# ------------------------- Routes -------------------------


@app.route("/")
def home():
    return render_template("index.html", home_url=url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template('login.html', home_url=url_for('home'))

        import re
        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email):
            flash("Invalid email format.", "danger")
            return render_template('login.html', home_url=url_for('home'))

        try:
            user = db.users.find_one({"email": email})
            if user and check_password_hash(user['password'], password):
                session.clear()
                session['user_id'] = str(user['_id'])
                session['username'] = user['username']
                print(
                    f"Session set: user_id={session['user_id']}, username={session['username']}")
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid email or password", "danger")
        except Exception as e:
            flash("An error occurred during login.", "danger")
            print(f"Login error: {e}")
    return render_template('login.html', home_url=url_for('home'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if not all([name, email, password, confirm_password]):
            flash("All fields are required!", "danger")
            return redirect(url_for("register"))

        if not '@' in email or not '.' in email:
            flash("Invalid email format.", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must be at least 8 characters long!", "danger")
            return redirect(url_for("register"))

        try:
            existing_user = db.users.find_one({"email": email})
            if existing_user:
                flash("Email already registered!", "danger")
                return redirect(url_for("register"))

            hashed_pw = generate_password_hash(password)
            joined_date = datetime.now().strftime("%Y-%m-%d")
            db.users.insert_one({
                "username": name,
                "email": email,
                "password": hashed_pw,
                "favorites": [],
                "joined": joined_date,
                "profile_picture": ""
            })
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash("An error occurred during registration.", "danger")
            print(f"Registration error: {e}")
    return render_template("register.html", home_url=url_for('home'))


@app.route("/dashboard")
def dashboard():
    print(f"Session on dashboard: {session}")
    if "user_id" not in session:
        flash("You must be logged in to access the dashboard.", "warning")
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"], home_url=url_for('home'), login_url=url_for('login'))


@app.route("/admin_panel")
def admin_panel():
    try:
        users = list(db.users.find())
        for user in users:
            user['_id'] = str(user['_id'])
            activities = list(db.activities.find(
                {"user_id": user['_id']}).sort("timestamp", -1).limit(5))
            user['activities'] = activities
        return render_template("admin.html", users=users, home_url=url_for('home'))
    except Exception as e:
        flash("Error loading admin panel.", "danger")
        print(f"Admin panel error: {e}")
        return render_template("admin.html", users=[], home_url=url_for('home'))


@app.route("/delete_user/<user_id>", methods=["POST"])
def delete_user(user_id):
    if "user_id" not in session:
        flash("You must be logged in to perform this action.", "warning")
        return redirect(url_for("login"))
    try:
        if user_id == session["user_id"]:
            flash("You cannot delete your own account from the admin panel.", "danger")
            return redirect(url_for("admin_panel"))

        db.users.delete_one({"_id": user_id})
        db.activities.delete_many({"user_id": user_id})
        flash("User deleted successfully.", "success")
    except Exception as e:
        flash("Error deleting user.", "danger")
        print(f"Delete user error: {e}")
    return redirect(url_for("admin_panel"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/contact")
def contact():
    return render_template("contact.html", home_url=url_for('home'))


@app.route("/submit_contact", methods=["POST"])
def submit_contact():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")
    if not all([name, email, message]):
        flash("All fields are required!", "danger")
        return redirect(url_for("contact"))

    if not '@' in email or not '.' in email:
        flash("Invalid email format.", "danger")
        return redirect(url_for("contact"))

    try:
        db.contacts.insert_one({
            "name": name,
            "email": email,
            "message": message,
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        flash("Thank you for reaching out! We’ll get back to you soon.", "success")
    except Exception as e:
        flash("Error submitting contact form.", "danger")
        print(f"Contact form error: {e}")
    return redirect(url_for("contact"))


@app.route("/get_user_data")
def get_user_data():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    try:
        user = db.users.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            return jsonify({
                "username": user["username"],
                "email": user["email"],
                "joined": user.get("joined", "N/A"),
                "profile_picture": user.get("profile_picture", "")
            })
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return jsonify({"error": "Server error"}), 500


@app.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    try:
        data = request.get_json()
        new_username = data.get("username")
        new_email = data.get("email")
        profile_picture = data.get("profile_picture")
        if not new_username or not new_email:
            return jsonify({"error": "Username and email are required"}), 400

        if not '@' in new_email or not '.' in new_email:
            return jsonify({"error": "Invalid email format"}), 400

        existing_user = db.users.find_one(
            {"email": new_email, "_id": {"$ne": ObjectId(session["user_id"])}})
        if existing_user:
            return jsonify({"error": "Email already in use"}), 400

        update_data = {"username": new_username, "email": new_email}
        if profile_picture:
            update_data["profile_picture"] = profile_picture

        result = db.users.update_one(
            {"_id": ObjectId(session["user_id"])},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            session["username"] = new_username
            return jsonify({"success": True, "username": new_username, "email": new_email, "profile_picture": profile_picture})
        return jsonify({"error": "No changes made"}), 400
    except Exception as e:
        print(f"Error updating profile: {e}")
        return jsonify({"error": "Server error"}), 500


@app.route("/get_favorites")
def get_favorites():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    try:
        user = db.users.find_one({"_id": ObjectId(session["user_id"])})
        return jsonify({"favorites": user.get("favorites", [])})
    except Exception as e:
        print(f"Error fetching favorites: {e}")
        return jsonify({"error": "Failed to fetch favorites"}), 500


@app.route("/toggle_favorite", methods=["POST"])
def toggle_favorite():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    data = request.get_json()
    type = data.get("type")
    item = data.get("item")
    action = data.get("action")
    if not all([type, item, action]) or type not in ["music", "event"]:
        return jsonify({"error": "Invalid request"}), 400

    try:
        user = db.users.find_one({"_id": ObjectId(session["user_id"])})
        favorites = user.get("favorites", [])
        fav_entry = {"type": type, "item": item}

        if action == "add" and fav_entry not in favorites:
            favorites.append(fav_entry)
        elif action == "remove" and fav_entry in favorites:
            favorites.remove(fav_entry)

        db.users.update_one({"_id": ObjectId(session["user_id"])}, {
                            "$set": {"favorites": favorites}})
        return jsonify({"success": True, "favorites": favorites})
    except Exception as e:
        print(f"Error toggling favorite: {e}")
        return jsonify({"error": "Failed to update favorites"}), 500


@app.route("/log_activity", methods=["POST"])
def log_activity():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    try:
        data = request.get_json()
        action = data.get("action")
        if not action:
            return jsonify({"error": "Action is required"}), 400
        activity = {
            "user_id": session["user_id"],
            "action": action,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        db.activities.insert_one(activity)
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error logging activity: {e}")
        return jsonify({"error": "Server error"}), 500


@app.route("/get_activity")
def get_activity():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    try:
        activities = list(db.activities.find(
            {"user_id": session["user_id"]}).sort("timestamp", -1).limit(5))
        for activity in activities:
            activity["_id"] = str(activity["_id"])
        return jsonify({"activities": activities})
    except Exception as e:
        print(f"Error fetching activity: {e}")
        return jsonify({"error": "Server error"}), 500


@app.route("/get_nostalgia_data/<year>")
@rate_limit
def get_nostalgia_data(year):
    if not year.isdigit() or int(year) < 1980 or int(year) > datetime.now().year:
        return jsonify({"error": "Invalid year. Must be between 1980 and current year."}), 400

    try:
        cached = db.nostalgia_data.find_one({"year": year})
        if cached:
            return jsonify(cached["data"])
    except Exception as e:
        print(f"Error fetching cached data: {e}")

    nostalgia_data = {"music": [], "events": [], "websites": []}

    billboard_url = f"https://www.billboard.com/charts/year-end/{year}/hot-100-songs/"
    soup = scrape_page(billboard_url)
    if soup:
        songs = soup.select('.o-chart-results-list__item .c-title')[:5]
        nostalgia_data["music"] = [song.get_text(
            strip=True) for song in songs if song.get_text(strip=True)]
    if not nostalgia_data["music"]:
        nostalgia_data["music"] = [
            f"Song {i} from {year}" for i in range(1, 6)]

    wiki_url = f"https://en.wikipedia.org/wiki/{year}"
    soup = scrape_page(wiki_url)
    if soup:
        events_section = soup.find('span', id='Events')
        if events_section:
            events_list = events_section.find_parent().find_next('ul')
            events = events_list.find_all('li')[:5] if events_list else []
            nostalgia_data["events"] = [
                event.get_text(strip=True) for event in events]
        if not nostalgia_data["events"]:
            paragraphs = soup.select('#mw-content-text p')[:5]
            nostalgia_data["events"] = [p.get_text(
                strip=True)[:100] + "..." for p in paragraphs if p.get_text(strip=True)]
    if not nostalgia_data["events"]:
        nostalgia_data["events"] = [
            f"Event {i} from {year}" for i in range(1, 6)]

    sites = [
        {"name": "Google", "url": "http://google.com"},
        {"name": "YouTube", "url": "http://youtube.com"},
        {"name": "Facebook", "url": "http://facebook.com"}
    ]
    for site in sites:
        try:
            api_url = f"https://archive.org/wayback/available?url={site['url']}&timestamp={year}0101000000"
            with urlopen(api_url, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                archived_url = (
                    data["archived_snapshots"]["closest"]["url"]
                    if data.get("archived_snapshots") and data["archived_snapshots"].get("closest")
                    else f"https://web.archive.org/web/{year}0101*/{site['url']}"
                )
                nostalgia_data["websites"].append(
                    {"name": site["name"], "url": archived_url})
        except (HTTPError, URLError) as e:
            print(f"Error fetching archive for {site['name']}: {e}")
            nostalgia_data["websites"].append({
                "name": site["name"],
                "url": f"https://web.archive.org/web/{year}0101*/{site['url']}"
            })

    try:
        db.nostalgia_data.update_one(
            {"year": year},
            {"$set": {"data": nostalgia_data}},
            upsert=True
        )
    except Exception as e:
        print(f"Error caching nostalgia data: {e}")
    return jsonify(nostalgia_data)


if __name__ == "__main__":
    if db is None:
        print("MongoDB not available. Exiting.")
    else:
        debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
        app.run(debug=debug_mode, port=5001)
