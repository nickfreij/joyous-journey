import openai
import os


from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Import SQL Database into web app
db = SQL("sqlite:///database.db")

# open ai api key
openai.api_key = "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"

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def home():
    "Homepage"
    if request.method == "GET":
        return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    "Register the user"

    if request.method == "POST":

        #make executable for full users list
        users = db.execute("SELECT * FROM users")

        #username checking
        if not request.form.get("username"):
            return apology("must provide username", 403)

        #password checking
        if not request.form.get("password"):
            return apology("must provide password", 403)

        #confirmation checking
        if not request.form.get("confirmation"):
            return apology("must provide confirmation", 403)

        elif (request.form.get("confirmation") != request.form.get("password")):
            return apology("must match passwords", 403)

        username = request.form.get("username")
        user_check = db.execute("SELECT username FROM users WHERE username = ?", username)

        if user_check:
            return apology("username already in use", 403)
        else:
            #generate hash
            password = request.form.get("password")
            password = generate_password_hash(password)

            #get height and weight
            height = request.form.get("height")
            height_unit = request.form.get("height_unit")
            weight = request.form.get("weight")
            weight_unit = request.form.get("weight_unit")

            #check if units are correct, then add to users
            if height_unit != ("in" or "cm"):
                return apology("incorrect unit use", 403)
            else:
                if weight_unit != ("lbs" or "kg"):
                    return apology("incorrect unit use", 403)
                else:
                    db.execute("INSERT INTO users (username, hash, height, weight, height_unit, weight_unit) VALUES (?, ?, ?, ?, ?, ?)", username, password, height, weight, height_unit, weight_unit)
                    return render_template("home.html")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any current user id
    session.clear()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        user_db = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(user_db) != 1 or not check_password_hash(user_db[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["userid"] = user_db[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/supplement", methods = ["GET", "POST"])
@login_required
def supplement():
    """make a prompt for the user to type in a supplement"""
    if request.method == "GET":
        return render_template("supplement.html")


    if request.method == "POST":
        supp = request.form.get("supp")

        #chat gpt prompt
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Can you please show me 1 study on the supplement called {supp} as it pertains to health and fitness and please give me the details on what they found? Please give it to me in 3 sentences max",
            temperature=1,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
            )
        return render_template("supplement.html", gptresponse = response)
        response = None

if __name__ == '__main__':
    app.run()