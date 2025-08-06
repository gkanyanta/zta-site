"""
Flask application for the Zambia Tennis Association website.

This simple app demonstrates how a novice developer can build a
membership‑driven website with basic functionality for a national sports
association.  The site uses Jinja2 templates for rendering pages, an
SQLite database for storing membership registrations and contact
messages, and a handful of hard‑coded lists to simulate news posts,
upcoming events and player rankings.  You can extend or replace these
lists with real data or connect to a more sophisticated content
management system when you're comfortable.

To run the development server locally, make sure you have Flask
installed (``pip install flask``), then execute ``python app.py`` in
the ``zta_website`` directory.  The site will be available at
``http://127.0.0.1:5000`` by default.
"""

from __future__ import annotations

import os
import sqlite3
import json
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET", "zta_secret_key")
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def init_db() -> None:
    """Create the SQLite database and necessary tables if they do not exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create members table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            category TEXT,
            address TEXT,
            age INTEGER,
            joined_at TEXT
        )
        """
    )
    # Create messages table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT,
            sent_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def insert_member(data: dict[str, str | int]) -> None:
    """Insert a new member record into the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO members (name, email, phone, category, address, age, joined_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("name"),
            data.get("email"),
            data.get("phone"),
            data.get("category"),
            data.get("address"),
            data.get("age"),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def insert_message(data: dict[str, str]) -> None:
    """Insert a contact form message into the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO messages (name, email, subject, message, sent_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data.get("name"),
            data.get("email"),
            data.get("subject"),
            data.get("message"),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


@app.context_processor
def inject_globals() -> dict[str, any]:
    """Inject common values into templates."""
    return {"current_year": datetime.utcnow().year}


# Sample data for demonstration purposes.  In a production system,
# these would likely come from a database or a content management system.
# News posts highlighting recent programmes and achievements.  These
# summaries are based on publicly available reports and social media
# updates from the association.  Dates are approximate and used for
# ordering posts chronologically.
SAMPLE_NEWS = [
    {
        "title": "IFS Invitational Youth Tournament showcases rising stars",
        "date": "2025-08-02",
        "summary": "The U12 & U14 IFS Invitational at Kansanshi Golf Estate delivered exciting matches and underscored the association’s commitment to youth development.",
        "content": (
            "Hosted at the picturesque Kansanshi Golf Estate in Solwezi, the IFS Invitational Tournament for under‑12 and under‑14 boys and girls brought together promising talent from across Zambia. "
            "Sponsored by International Facilities Services (IFS) in collaboration with Kansanshi Mining Project, the event offered high‑quality playing opportunities and emphasised sportsmanship and passion for the game. "
            "Match results and standings were shared throughout the tournament, and parents, coaches and officials applauded the young athletes’ dedication."
        ),
    },
    {
        "title": "Copperbelt Open finals produce new champions",
        "date": "2025-08-04",
        "summary": "After four days of thrilling tennis in Kitwe, the Copperbelt Open crowned new champions in both the men’s and women’s divisions.",
        "content": (
            "The Copperbelt Open, hosted at Nkana Tennis Club, culminated in a dramatic finals day. "
            "Spectators witnessed intense rallies and tactical play as emerging players seized their moment to lift the national titles. "
            "The tournament showcased the depth of talent in Zambian tennis and provided valuable ranking points ahead of forthcoming national events."
        ),
    },
    {
        "title": "Ladies trials set stage for 2024 All Africa Games",
        "date": "2023-12-27",
        "summary": "Trials at Nkana Tennis Club determined which female players would represent Zambia at the All Africa Games in Accra.",
        "content": (
            "In the closing days of 2023, the association organised women’s trials to select representatives for the 2024 All Africa Games in Ghana. "
            "The round‑robin format produced competitive matches and highlighted the growing depth of women’s tennis in Zambia. "
            "The trials underline the association’s commitment to equal opportunities and preparing athletes for continental competition."
        ),
    },
    {
        "title": "MIKA Hotels invests in seventh international championship",
        "date": "2023-10-20",
        "summary": "A £500,000 sponsorship from MIKA Hotels boosted the 7th MIKA Tennis Championships, attracting players from nine countries.",
        "content": (
            "Held at Lusaka Tennis Club, the 2023 MIKA International Championships drew around 120 participants from Zambia and eight neighbouring countries. "
            "The significant sponsorship from MIKA Hotels enabled higher prize money and improved facilities, enhancing the event’s stature. "
            "The tournament provided a platform for local athletes to test themselves against regional competitors and showcased Zambia as a growing hub for tennis in Southern Africa."
        ),
    },
    {
        "title": "Junior champions crowned at Mike Mambwe Memorial",
        "date": "2023-09-20",
        "summary": "Thrilling finals at the Mike Mambwe Junior Championship saw young players claim titles in the U10 and U14 categories.",
        "content": (
            "The Mike Mambwe Junior Championship in Ndola celebrated promising talent across the under‑10 and under‑14 divisions. "
            "In the U10 final, a three‑set battle kept spectators on edge before a determined young player clinched victory in a match tie‑break. "
            "The U14 girls’ final was equally competitive, with the champion prevailing 6–4, 7–5 after an impressive run through the draw. "
            "These grassroots events reflect the association’s dedication to nurturing junior players and providing competitive opportunities across age groups."
        ),
    },
    {
        "title": "Association recognised for successful 2024 AGM",
        "date": "2024-12-16",
        "summary": "The National Olympic Committee of Zambia congratulated the association on its well‑organised Annual General Meeting.",
        "content": (
            "In December 2024 the National Olympic Committee of Zambia (NOCZ) publicly congratulated the Zambia Tennis Association on hosting a successful Annual General Meeting. "
            "The recognition reflects improved governance under the current executive committee and encourages continued collaboration with stakeholders to grow the sport nationwide."
        ),
    },
]


# Try to load official events data from JSON file.  The file is generated from
# the provisional calendar PDF.  Fallback to a small default list if it does
# not exist.
DEFAULT_EVENTS = [
    {
        "title": "National Championships",
        "start": "2025-08-20",
        "end": "2025-08-24",
        "location": "Lusaka National Tennis Centre",
        "category": "ZTA SENIOR",
        "description": "The annual national championships featuring singles and doubles events for men and women."
    },
    {
        "title": "Youth Development Camp",
        "start": "2025-09-15",
        "end": "2025-09-19",
        "location": "Copperbelt Tennis Academy, Ndola",
        "category": "TRAINING",
        "description": "A training camp for junior players focusing on skill development, fitness and mental preparation."
    },
    {
        "title": "Coaches Certification Course",
        "start": "2025-10-05",
        "end": "2025-10-08",
        "location": "Livingstone Sports Complex",
        "category": "TRAINING",
        "description": "An ITF accredited certification course for tennis coaches seeking to upgrade their qualifications."
    },
]

# Load events from data/events.json if available
events_file = os.path.join(os.path.dirname(__file__), 'data', 'events.json')
if os.path.exists(events_file):
    try:
        with open(events_file, 'r') as f:
            EVENTS = json.load(f)
    except Exception:
        EVENTS = DEFAULT_EVENTS
else:
    EVENTS = DEFAULT_EVENTS


SAMPLE_RANKINGS = [
    {"rank": 1, "player": "Chanda Mwila", "points": 1580},
    {"rank": 2, "player": "Mwila Phiri", "points": 1420},
    {"rank": 3, "player": "Josephine Banda", "points": 1375},
    {"rank": 4, "player": "Richard Njobvu", "points": 1290},
    {"rank": 5, "player": "Grace Tembo", "points": 1205},
]


@app.route("/")
def index() -> str:
    """Render the home page with latest news and upcoming events."""
    news_preview = SAMPLE_NEWS[:3]
    # Select the next few upcoming events sorted by start date
    try:
        # Sort EVENTS by start date string
        events_sorted = sorted(EVENTS, key=lambda e: e["start"])
    except Exception:
        events_sorted = EVENTS
    events_preview = events_sorted[:6] if events_sorted else []
    return render_template(
        "index.html",
        title="Home",
        news=news_preview,
        events=events_preview,
    )


@app.route("/about")
def about() -> str:
    """Render the about page."""
    return render_template("about.html", title="About")


@app.route("/news")
def news() -> str:
    """Render the news page with all posts."""
    return render_template("news.html", title="News", posts=SAMPLE_NEWS)


@app.route("/events")
def events() -> str:
    """Render the events page."""
    return render_template("events.html", title="Events", events=EVENTS)


@app.route("/api/events")
def api_events() -> any:
    """Return events as JSON for the calendar widget."""
    return jsonify(EVENTS)


@app.route("/ranking")
def ranking() -> str:
    """Render the ranking page."""
    return render_template("ranking.html", title="Rankings", rankings=SAMPLE_RANKINGS)


@app.route("/membership", methods=["GET", "POST"])
def membership() -> str:
    """Render the membership page and handle registration form submissions."""
    if request.method == "POST":
        form = request.form
        # Basic validation: ensure required fields are present
        name = form.get("name").strip() if form.get("name") else None
        email = form.get("email").strip() if form.get("email") else None
        if not name or not email:
            flash("Name and email are required.", "danger")
        else:
            try:
                insert_member(
                    {
                        "name": name,
                        "email": email,
                        "phone": form.get("phone"),
                        "category": form.get("category"),
                        "address": form.get("address"),
                        "age": int(form.get("age")) if form.get("age") else None,
                    }
                )
                flash("Thank you for registering! We will contact you soon.", "success")
            except Exception as e:
                flash(f"Error saving your registration: {e}", "danger")
        return redirect(url_for("membership"))
    return render_template("membership.html", title="Membership")


@app.route("/contact", methods=["GET", "POST"])
def contact() -> str:
    """Render the contact page and handle contact form submissions."""
    if request.method == "POST":
        form = request.form
        name = form.get("name").strip() if form.get("name") else None
        email = form.get("email").strip() if form.get("email") else None
        if not name or not email:
            flash("Name and email are required.", "danger")
        else:
            try:
                insert_message(
                    {
                        "name": name,
                        "email": email,
                        "subject": form.get("subject"),
                        "message": form.get("message"),
                    }
                )
                flash("Thank you for contacting us. We will respond shortly.", "success")
            except Exception as e:
                flash(f"Error sending your message: {e}", "danger")
        return redirect(url_for("contact"))
    return render_template("contact.html", title="Contact")


# Veterans (Madalas) gallery
@app.route("/veterans")
def veterans_gallery() -> str:
    """Display a gallery of images for the Veterans (Madalas) category."""
    # List image filenames in the veterans static directory
    gallery_dir = os.path.join(app.static_folder, 'images', 'veterans')
    try:
        files = [f for f in os.listdir(gallery_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        # Sort by filename for consistent order
        files.sort()
    except Exception:
        files = []
    # Build URL paths for templates
    image_urls = [url_for('static', filename=f'images/veterans/{fname}') for fname in files]
    return render_template('veterans.html', title='Veterans', images=image_urls)

# Juniors gallery
@app.route("/juniors")
def juniors_gallery() -> str:
    """Display a gallery of images for the Juniors category."""
    gallery_dir = os.path.join(app.static_folder, 'images', 'juniors')
    try:
        files = [f for f in os.listdir(gallery_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        files.sort()
    except Exception:
        files = []
    image_urls = [url_for('static', filename=f'images/juniors/{fname}') for fname in files]
    return render_template('juniors.html', title='Juniors', images=image_urls)

# Seniors gallery
@app.route("/seniors")
def seniors_gallery() -> str:
    """Display a gallery of images for the Seniors category."""
    gallery_dir = os.path.join(app.static_folder, 'images', 'seniors')
    try:
        files = [f for f in os.listdir(gallery_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        files.sort()
    except Exception:
        files = []
    image_urls = [url_for('static', filename=f'images/seniors/{fname}') for fname in files]
    return render_template('seniors.html', title='Seniors', images=image_urls)


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
