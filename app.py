from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import send_file

from flask_sqlalchemy import SQLAlchemy

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import styles
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

from datetime import datetime

import random
import os


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


app.config[
"SQLALCHEMY_DATABASE_URI"
] = database_url


app.config[
"SQLALCHEMY_TRACK_MODIFICATIONS"
] = False


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

    error=""

    if request.method=="POST":

        username=request.form.get(
        "username"
        )

        password=request.form.get(
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

        UnicodeCIDFont(
        "STSong-Light"
        )

    )


    style=styles.getSampleStyleSheet()

    style["Title"].fontName="STSong-Light"
    style["Heading2"].fontName="STSong-Light"
    style["Normal"].fontName="STSong-Light"


    content=[]


    content.append(

    Paragraph(

    "ОТЧЁТ СИСТЕМЫ ОЧИСТКИ БЫТОВЫХ СТОЧНЫХ ВОД",

    style["Title"]

    )

    )


    content.append(
    Spacer(1,20)
    )


    content.append(

    Paragraph(

    f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",

    style["Normal"]

    )

    )


    content.append(

    Paragraph(

    "Объект: Очистные сооружения бытовых сточных вод",

    style["Normal"]

    )

    )


    content.append(
    Spacer(1,20)
    )



    history=History.query.order_by(

    History.id.desc()

    ).limit(
    10
    ).all()



    content.append(

    Paragraph(

    "История параметров",

    style["Heading2"]

    )

    )


    table_data=[]


    table_data.append(

    [
    "Уровень",
    "Температура"
    ]

    )


    for row in history:

        table_data.append(

        [

        f"{row.water}%",

        f"{row.temperature}°C"

        ]

        )


    table=Table(
    table_data
    )


    table.setStyle(

    TableStyle([

    ('GRID',(0,0),(-1,-1),1,colors.black),

    ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),

    ('FONTNAME',(0,0),(-1,-1),'STSong-Light'),

    ('ALIGN',(0,0),(-1,-1),'CENTER')

    ])

    )


    content.append(
    table
    )



    content.append(
    Spacer(1,20)
    )



    alarms=Alarm.query.order_by(

    Alarm.id.desc()

    ).limit(
    5
    ).all()



    content.append(

    Paragraph(

    "Журнал аварий",

    style["Heading2"]

    )

    )


    alarm_data=[]


    alarm_data.append(

    [
    "Время",
    "Событие"
    ]

    )


    for alarm in alarms:

        alarm_data.append(

        [
        alarm.time,
        alarm.message
        ]

        )


    alarm_table=Table(
    alarm_data
    )


    alarm_table.setStyle(

TableStyle([

('GRID',(0,0),(-1,-1),1,colors.black),

('BACKGROUND',(0,0),(-1,0),colors.lightgrey),

('FONTNAME',(0,0),(-1,-1),'STSong-Light'),

('ALIGN',(0,0),(-1,-1),'CENTER')

])

)



    content.append(
    alarm_table
    )


    content.append(
    Spacer(1,40)
    )


    content.append(

    Paragraph(

    "Подпись оператора: __________________",

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



@app.route("/receive", methods=["GET","POST"])
def receive():

    water = request.values.get(
        "water"
    )

    temperature = request.values.get(
        "temperature"
    )

    if water and temperature:

        record = History(

            water=int(water),
            temperature=int(temperature)

        )

        db.session.add(
            record
        )

        db.session.commit()

        return "OK"

    return "READY"


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