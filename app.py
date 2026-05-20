from flask import Flask, render_template

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
    "mode":"Автоматический",

    "alarm":"Аварий не обнаружено",

    "events":[
        "12:30 Система запущена",
        "12:34 Получены данные от ПЛК",
        "12:36 Насос №1 включен",
        "12:40 Передано SMS-сообщение"
    ]
}

@app.route("/")
def index():
    return render_template("index.html", data=data)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)