from flask import Flask, render_template
import os

app = Flask(__name__)

data = {

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


@app.route("/")
def index():

    return render_template(
        "index.html",
        data=data
    )


if __name__=="__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )