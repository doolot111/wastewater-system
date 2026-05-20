from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import random
import os

app = Flask(__name__)

app.secret_key = "wastewater_secret"

# Вместо жёсткой вставки адреса БД используем переменную окружения
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class History(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    water = db.Column(
        db.Integer
    )

    temperature = db.Column(
        db.Integer
    )


with app.app_context():
    db.create_all()


data = {

    "modicon":"Подключен",
    "br":"Подключен",
    "tc65":"В сети",
    "operator":"MegaCom",
    "signal":"25",

    "flow":"12",
    "ph":"7.2",

    "pump1":"Включен",
    "pump2":"Выключен",
    "aerator":"Включен",
    "mode":"Автоматический"

}


@app.route("/", methods=["GET","POST"])
def login():

    error = ""

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )

        if username=="admin" and password=="12345":

            session["user"]=username

            return redirect(
                "/dashboard"
            )

        else:

            error="Неверный логин или пароль"

    return render_template(
        "login.html",
        error=error
    )


@app.route("/dashboard")
def dashboard():

    if "user" not in session:

        return redirect("/")


    water = random.randint(
        60,
        90
    )

    temperature = random.randint(
        20,
        30
    )


    record = History(

        water=water,
        temperature=temperature

    )

    db.session.add(
        record
    )

    db.session.commit()


    history = History.query.order_by(
        History.id.desc()
    ).limit(
        10
    ).all()


    data["water_level"]=water
    data["temperature"]=temperature


    return render_template(
        "index.html",
        data=data,
        history=history
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__=="__main__":

    port=int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )