from flask import Flask, request

import inspect


app = Flask(__name__)


def zabbix():
    from healthcheck.backends import Zabbix
    return Zabbix()


@app.route("/url", methods=["POST"])
def add_url():
    name = request.form.get("name")
    url = request.form.get("url")
    zabbix().add_url(name, url)
    return "", 201


@app.route("/<name>/url/<path:url>", methods=["DELETE"])
def remove_url(name, url):
    zabbix().remove_url(name, url)
    return "", 204


@app.route("/watcher", methods=["POST"])
def add_watcher():
    name = request.form.get("name")
    watcher = request.form.get("watcher")
    zabbix().add_watcher(name, watcher)
    return "", 201


@app.route("/<name>/watcher/<watcher>", methods=["DELETE"])
def remove_watcher(name, watcher):
    zabbix().remove_watcher(name, watcher)
    return "", 204


@app.route("/", methods=["POST"])
def new():
    name = request.form.get("name")
    zabbix().new(name)
    return "", 201


@app.route("/<name>", methods=["DELETE"])
def remove(name):
    zabbix().remove(name)
    return "", 204


@app.route("/plugin", methods=["GET"])
def plugin():
    from healthcheck import plugin
    source = inspect.getsource(plugin)
    return source, 200
