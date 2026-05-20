from flask import Flask, render_template, request, redirect, session
import os

app = Flask(__name__)

app.secret_key="wastewater123"

data={

"modicon":"Подключен",
"br":"Подключен",
"tc65":"В сети",
"operator":"MegaCom",
"signal":"25",

"water_level":"68",
"flow":"12",
"temperature":"24",
"ph":"7.2",

"pump1":"Включен",
"pump2":"Выключен",
"aerator":"Включен",
"mode":"Автоматический"

}


@app.route("/",methods=["GET","POST"])

def login():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        if username=="admin" and password=="12345":

            session["user"]=username

            return redirect("/dashboard")

    return render_template(
        "login.html"
    )


@app.route("/dashboard")
def dashboard():

    if "user" not in session:

        return redirect("/")

    return render_template(
        "index.html",
        data=data
    )


@app.route("/logout")
def logout():

    session.pop(
        "user",
        None
    )

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