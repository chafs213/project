from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
#from datetime import date

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    table_symbols = db.execute("SELECT symbol, shares FROM tablebase WHERE id=:id",id=session["user_id"])
    all_cash = 0
    for table_symbol in table_symbols:
        symbol = table_symbol["symbol"]
        shares = table_symbol["shares"]
        stock = lookup(symbol)
        total_cash = float(shares) * float(stock["price"])
        all_cash = all_cash + total_cash
        db.execute("UPDATE tablebase SET price =:price, total=:total WHERE id=:id AND symbol=:symbol",price = usd(stock["price"]),total=usd(total_cash),id=session["user_id"],symbol =symbol)
    cash = db.execute("SELECT cash FROM users WHERE id=:id",id=session["user_id"])
    casher = cash[0]["cash"]
    all_cash+= casher
    tablesymbols = db.execute("SELECT * FROM tablebase WHERE id=:id",id=session["user_id"])
    return render_template("index.html",stocks = tablesymbols,cash = usd(casher),total = usd(all_cash) )








@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    if request.method == "GET":
        return render_template("buy.html")
    else:
        # ensure proper symbol
        stock = lookup(request.form.get("symbol"))
        if not stock:
            return apology("Invalid Symbol")

        # ensure proper number of shares
        try:
            shares = int(request.form.get("shares"))
            if shares < 0:
                return apology("Shares must be positive integer")
        except:
            return apology("Shares must be positive integer")

        # select user's cash
        money = db.execute("SELECT cash FROM users WHERE id = :id", \
                            id=session["user_id"])

        # check if enough money to buy
        if not money or float(money[0]["cash"]) < stock["price"] * shares:
            return apology("Not enough money")

        # update history

        db.execute("INSERT INTO purchases (symbol, share, price, id) \
                    VALUES(:symbol, :share, :price, :id)", \
                    symbol=stock["symbol"], share=shares, \
                    price=usd(stock["price"]), id=session["user_id"])

        # update user cash
        db.execute("UPDATE users SET cash = cash - :purchase WHERE id = :id", \
                    id=session["user_id"], \
                    purchase=stock["price"] * float(shares))

        # Select user shares of that symbol
        user_shares = db.execute("SELECT shares FROM tablebase \
                           WHERE id = :id AND symbol=:symbol", \
                           id=session["user_id"], symbol=stock["symbol"])

        # if user doesn't has shares of that symbol, create new stock object
        if not user_shares:
            db.execute("INSERT INTO tablebase (id, name, symbol, shares, price, total) \
                        VALUES(:id, :name, :symbol, :shares, :price, :total)", \
                        id=session["user_id"],name=stock["name"],symbol=stock["symbol"], shares=shares, price=usd(stock["price"]), \
                        total=usd(shares * stock["price"]))

        # Else increment the shares count
        else:
            shares_total = user_shares[0]["shares"] + shares
            db.execute("UPDATE tablebase SET shares=:shares \
                        WHERE id=:id AND symbol=:symbol", \
                        shares=shares_total, id=session["user_id"], \
                        symbol=stock["symbol"])
            total_price = int(shares_total) * float(stock["price"])
            db.execute("UPDATE tablebase SET total=:total \
                        WHERE id=:id", \
                        total=usd(total_price), id=session["user_id"]
                        )

        # return to index
        return redirect(url_for("index"))

@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    history = db.execute("SELECT * FROM purchases WHERE id=:id",id=session["user_id"])
    return render_template("history.html",history = history)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))


@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        if request.form["username"] == "" or request.form["password"] == "" or request.form["confirmpassword"]=="":
            return apology("must provide username")
        elif not request.form["password"] == request.form["confirmpassword"]:
            return apology("must provide same password not match")
        else:
            hash = request.form.get("password")
            hash= pwd_context.hash(hash)
            result = db.execute("INSERT INTO users (username,hash) VALUES(:username,:hash)",username=request.form.get("username"),hash=hash)
            if not result:
                return apology("already exists")
            session["user_id"] = result
            return redirect(url_for("index"))



    else:
        return render_template("register.html")

@app.route("/add",methods=["GET","POST"])
@login_required
def add():
    if request.method== "POST":
        money = float(request.form.get("add"))
        db.execute("UPDATE users SET cash = cash + :money WHERE id=:id",money = money,id=session["user_id"])
        return redirect(url_for("index"))
    else:
        return render_template("add.html")


@app.route("/changepass",methods=["GET","POST"])
@login_required
def changepass():
    if request.method == "POST":
        passwords = db.execute("UPDATE users SET hash=:password WHERE id=:id", password = pwd_context.hash(request.form.get("changepass")),id=session["user_id"])
        return redirect(url_for("index"))
    else:

        return render_template("changepass.html")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        rows = lookup(request.form.get("symbol"))
        if not rows:
            return apology("INvalid symbol")
        return render_template("quoted.html",stock= rows)
    else:
        return render_template("quote.html")




@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    if request.method =="POST":
        stock = lookup(request.form.get("symbol"))
        user_shares = db.execute("SELECT shares FROM tablebase \
                           WHERE id = :id AND symbol=:symbol", \
                           id=session["user_id"], symbol=stock["symbol"])
        shares_total = int(user_shares[0]["shares"])
        if shares_total <= int(request.form.get("shares")):
            return apology("you don´t own that much shares")
        else:

            #mate_price = db.execute("SELECT price FROM tablebase WHERE id=:id AND symbol=:symbol",id=session["user_id"],symbol=stock["symbol"])
            share_sold = int(request.form.get("shares")) * float(stock["price"])
            db.execute("UPDATE tablebase SET shares=:shares WHERE id=:id AND symbol=:symbol",shares = shares_total - int(request.form.get("shares")),id=session["user_id"],symbol=stock["symbol"])
            #casher = db.execute("SELECT cash FROM users WHERE id=:id",id=session["user_id"])
            db.execute("INSERT INTO purchases (symbol, share, price, id) VALUES(:symbol, :share, :price, :id) ",symbol=stock["symbol"],share= -int(request.form.get("shares")),price = stock["price"],id=session["user_id"])

            db.execute("UPDATE users SET cash = cash + :casher WHERE id=:id",casher = share_sold , id=session["user_id"])

            return redirect(url_for("index"))





    else:

        symbolstable = db.execute("SELECT symbol FROM tablebase WHERE id=:id",id=session["user_id"])
        for symbolstab in symbolstable:
            symbol = symbolstab["symbol"]
            stock = lookup(symbol)

        tablesymbols = db.execute("SELECT * FROM tablebase WHERE id=:id",id=session["user_id"])
        return render_template("sell.html",stocks = tablesymbols)


