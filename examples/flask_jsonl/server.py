# -*- coding: utf-8 -*-

import flask

import flask_jsonl

jsonl_app = flask_jsonl.FlaskJsonl()

app = flask.Flask(__name__)
jsonl_app.init_app(app)


def fetch(count):
    for i in range(count):
        yield {"id": i, "title": "One Hundred Years of Solitude"}


@app.route("/api/data/<int:count>/", methods=["GET"])
def dump_jsonl_stream(count):
    return jsonl_app.response(fetch(count))


@app.route("/api/data/", methods=["POST"])
def dump_loaded_jsonl_stream():
    return jsonl_app.response(jsonl_app.load())


if __name__ == "__main__":
    app.run(debug=True)
