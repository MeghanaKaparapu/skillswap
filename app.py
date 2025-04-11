from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from models import create_offer_document, match_offers, hash_password, verify_password

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/skillswap"
app.secret_key = 'your_secret_key_here'  # change in production
mongo = PyMongo(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        existing_user = mongo.db.users.find_one({"username": username})

        if existing_user:
            flash("Username already exists.")
            return redirect(url_for('signup'))

        hashed_pw = hash_password(password)
        mongo.db.users.insert_one({"username": username, "password": hashed_pw})
        session['username'] = username
        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = mongo.db.users.find_one({"username": username})

        if user and verify_password(user['password'], password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials.")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('logout.html')


@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    unmatched_offers = list(mongo.db.skills.find({"matched": False}))
    matched_offers = list(mongo.db.skills.find({"matched": True}))
    return render_template('index.html', offers=unmatched_offers, matched_offers=matched_offers)

@app.route('/add', methods=['POST'])
def add_offer():
    if 'username' not in session:
        return redirect(url_for('login'))

    skill_offer = request.form['skill_offer']
    skill_want = request.form['skill_want']
    new_offer = create_offer_document(session['username'], skill_offer, skill_want)
    mongo.db.skills.insert_one(new_offer)
    return redirect(url_for('index'))

@app.route('/match')
def match():
    if 'username' not in session:
        return redirect(url_for('login'))

    unmatched = list(mongo.db.skills.find({"matched": False}))
    matches = match_offers(unmatched)

    matched_ids = set()
    for m in matches:
        for offer in unmatched:
            if (
                (offer["user"] == m["user1"] and offer["skill_offer"] == m["user1_offers"] and offer["skill_want"] == m["user1_wants"]) or
                (offer["user"] == m["user2"] and offer["skill_offer"] == m["user2_offers"] and offer["skill_want"] == m["user2_wants"])
            ):
                matched_ids.add(offer["_id"])

    for _id in matched_ids:
        mongo.db.skills.update_one({"_id": _id}, {"$set": {"matched": True}})

    return render_template('matches.html', matches=matches)

if __name__ == '__main__':
    app.run(debug=True)
