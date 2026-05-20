from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import styles

from flask import Flask, render_template
from flask import request, redirect
from flask import session, send_file

from flask_sqlalchemy import SQLAlchemy

import random
import os

from datetime import datetime


app = Flask(__name__)

app.secret_key = "wastewater_secret"


database_url = os.environ.get(
    "DATABASE_URL"
)

if database_url:

    database_url = database_url.replace(
        "postgresql://",
        "postgresql+psycopg2://",
        1
    )


app.config["SQLALCHEMY_DATABASE_URI"] = database_url

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



class Alarm(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    message = db.Column(
        db.String(200)
    )

    time = db.Column(
        db.String(50)
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



@app.route(
"/",
methods=["GET","POST"]
)

def login():

    error = ""

    if request.method=="POST":

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


    water=random.randint(
    60,
    95
    )

    temperature=random.randint(
    20,
    30
    )


    record=History(

    water=water,
    temperature=temperature

    )


    db.session.add(
    record
    )


    if water>85:

        alarm=Alarm(

        message=
        "Высокий уровень сточных вод",

        time=
        datetime.now().strftime(
        "%d.%m.%Y %H:%M:%S"
        )

        )

        db.session.add(
        alarm
        )


    db.session.commit()


    history=History.query.order_by(

    History.id.desc()

    ).limit(
    10
    ).all()



    alarms=Alarm.query.order_by(

    Alarm.id.desc()

    ).limit(
    5
    ).all()



    data["water_level"]=water

    data["temperature"]=temperature



    return render_template(

    "index.html",

    data=data,

    history=history,

    alarms=alarms

    )



@app.route("/logout")

def logout():

    session.clear()

    return redirect("/")



@app.route("/report")

def report():

    if "user" not in session:

        return redirect("/")


    file="report.pdf"

    doc=SimpleDocTemplate(
    file
    )


    pdfmetrics.registerFont(

    TTFont(
    "Vera",
    "Vera.ttf"
    )

    )


    style=styles.getSampleStyleSheet()

    style["Title"].fontName="Vera"
    style["Heading2"].fontName="Vera"
    style["Normal"].fontName="Vera"


    content=[]


    content.append(

    Paragraph(

    "Отчёт системы очистки бытовых сточных вод",

    style["Title"]

    )

    )


    content.append(

    Spacer(
    1,
    20
    )

    )


    history=History.query.order_by(

    History.id.desc()

    ).limit(
    10
    ).all()


    alarms=Alarm.query.order_by(

    Alarm.id.desc()

    ).limit(
    5
    ).all()



    content.append(

    Paragraph(

    "История параметров",

    style["Heading2"]

    )

    )


    for row in history:

        content.append(

        Paragraph(

        f"Уровень: {row.water}% | Температура: {row.temperature}°C",

        style["Normal"]

        )

        )



    content.append(

    Spacer(
    1,
    20
    )

    )



    content.append(

    Paragraph(

    "Журнал аварий",

    style["Heading2"]

    )

    )



    for alarm in alarms:

        content.append(

        Paragraph(

        f"{alarm.time} : {alarm.message}",

        style["Normal"]

        )

        )


    doc.build(
    content
    )


    return send_file(

    file,

    as_attachment=True

    )



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