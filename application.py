import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    """user_id = session["user_id"]"""

    books = db.execute("SELECT * FROM books")

    return render_template("index.html", books=books)


@app.route("/newbook", methods=["GET", "POST"])
@login_required
def newbook():
    """Buy shares of stock"""
    if request.method == "POST":
        book_title = request.form.get("book_title")
        book_author = request.form.get("book_author")
        publish_year = request.form.get("publish_year")
        language = request.form.get("language")
        if not book_title:
            return apology("Please enter a title")
        elif not book_author:
            return apology("Please enter an author")
        if not publish_year:
            return apology("Please insert the year of creation!")
        try:
            publish_year = int(request.form.get("publish_year"))
        except:
            return apology("Publish year must be an Integer!")

        if publish_year <= 0:
            return apology("Year must be more than zero!")

        """user_id = session["user_id"]"""

        db.execute("INSERT INTO books (book_title, book_author, publish_year, language) VALUES (?, ?, ?, ?)",
                   book_title, book_author, publish_year, language)

        return redirect('/')
    else:
        return render_template("newbook.html")


@app.route("/library")
@login_required
def library():
    """Show library of transactions"""

    user_id = session["user_id"]

    books = db.execute("SELECT * FROM books")

    return render_template("library.html", books=books)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM admins WHERE admin_name = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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


"""@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    Get stock quote.
    if (request.method == "POST"):
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Please insert a Symbol")
        item = lookup(symbol)

        if not item:
            return apology("Invalid Symbol")
        return render_template("quoted.html", item=item, usd=usd)
    else:
        return render_template("quote.html")"""


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Please enter a username!")
        elif not password:
            return apology("Please enter a password!")
        elif not confirmation:
            return apology("Password confirmation required!")

        if password != confirmation:
            return apology("Password do not match!")

        hash = generate_password_hash(password)

        db.execute("INSERT INTO admins (admin_name, hash) VALUES (?, ?)", username, hash)
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    """Sell shares of stock"""

    if request.method == "POST":
        user_id = session["user_id"]
        book_id = request.form.get("book_id")
        db.execute("DELETE FROM books WHERE id = ?", book_id)
        return redirect("/")
    else:
        user_id = session["user_id"]
        return render_template("remove.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search For a book in database"""
    if request.method == "POST":
        book_title = request.form.get("book_title")
        book_author = request.form.get("book_author")
        publish_year = request.form.get("publish_year")
        language = request.form.get("language")

        search_book = db.execute("SELECT * FROM books WHERE book_title = ? OR book_author = ? OR publish_year = ? OR language = ?",
                                  book_title, book_author, publish_year, language)

        return render_template("searched.html", books=search_book)
    else:
        return render_template("search.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)