from flask import Flask
import os
import requests
import json
from flask import request
import logging

app = Flask(__name__)
app.config.from_pyfile('settings.py')


user = app.config.get("SHINOBI_USERNAME", "admin")
pw = app.config.get("SHINOBI_PASSWORD", "admin")
machine = "proxy"
function = "dash"
api=app.config.get("API_KEY", "api")
group=app.config.get("API_GROUP", "grp")
url = app.config.get("SHINOBI_URL", "http://localhost:8080")




@app.route('/tg_state')
def get_tg_state():
    data = {"machineID": machine, "mail": user, "pass": pw, "function": function}
    res = requests.post(f'{url}/?json=true', json=data)
    json_data = json.loads(res.text)
    logging.debug(json_data["$user"]["details"]["telegrambot"])
    if json_data["$user"]["details"]["telegrambot"] == 1:
        return {"is_active": "true"}
    elif json_data["$user"]["details"]["telegrambot"] == 0:
        return {"is_active": "false"}
    else:
        return json_data
    

@app.route('/tg_toggle', methods=['POST'])
def set_tg_state():
    req = request.json
    logging.debug(req)
    toggle=0
    if req["active"] == "true":
        toggle=1
    data = {"data": {"details": {"telegrambot":toggle}}}
    logging.debug(data)
    res = requests.post(f'{url}/{api}/accounts/{group}/edit', json=data)
    logging.debug(res.content)
    return 'Ok'





