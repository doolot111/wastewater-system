from flask import Flask, render_template, request, redirect, session
import sqlite3
import random
import os

app = Flask(__name__)

app.secret_key="wastewater_secret"

data={

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


def create_db():

    conn=sqlite3.connect(
        "system.db"
    )

    cursor=conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS history(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    water INTEGER,

    temperature INTEGER

    )

    """)

    conn.commit()

    conn.close()


create_db()


@app.route("/",methods=["GET","POST"])
def login():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        if username=="admin" and password=="12345":

            session["user"]=username

            return redirect(
                "/dashboard"
            )

    return render_template(
        "login.html"
    )


@app.route("/dashboard")
def dashboard():

    if "user" not in session:

        return redirect("/")


    water=random.randint(
        60,
        90
    )

    temperature=random.randint(
        20,
        30
    )


    conn=sqlite3.connect(
        "system.db"
    )

    cursor=conn.cursor()

    cursor.execute(
    """

    INSERT INTO history(
    water,
    temperature
    )

    VALUES(?,?)

    """,

    (
    water,
    temperature
    )

    )

    conn.commit()


    cursor.execute(
    """

    SELECT water,
    temperature

    FROM history

    ORDER BY id DESC

    LIMIT 10

    """
    )

    history=cursor.fetchall()

    conn.close()


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