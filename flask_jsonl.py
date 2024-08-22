try:
    import flask
    import werkzeug.exceptions
except ImportError:
    raise ValueError("It is required to install 'flask' if you wish to use this module.") from None

import jsonl as provider


class FlaskJsonl:
    """
    Flask extension to support consuming and producing jsonlines data.
    ¡Experimental!
    """

    def __init__(self, app=None, mimetype="application/jsonl"):
        self.provider = provider
        self.mimetype = mimetype
        if app:
            self.init_app(app)

    def init_app(self, app):
        # Configure the jsonlines provider according to the given Flask app.
        self.provider.json_dumps = app.json.dumps
        self.provider.json_loads = app.json.loads

    def response(self, *args, **kwargs):
        """
        Dump data to a jsonlines stream response.

        :param args: args to pass to the 'flask.app.json.dumps' method.
        :param kwargs: kwargs to pass to the 'flask.app.json.dumps' method.
        :rtype: flask.Response
        """

        stream = flask.stream_with_context(self.provider.dumper(*args, **kwargs))
        response = flask.Response(stream)
        response.mimetype = self.mimetype
        return response

    def load(self, **kwargs):
        """
        Load jsonlines data from the Flask request stream.

        :param dict kwargs: kwargs to pass to the 'flask.app.json.loads' method.
        :rtype: Iterable[any]
        """

        if flask.request.mimetype == self.mimetype:
            return self.provider.load(flask.request.stream, **kwargs)
        else:
            raise werkzeug.exceptions.UnsupportedMediaType
