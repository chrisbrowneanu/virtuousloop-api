from flask import Flask, Response, jsonify, request, render_template
import logging

from .errors import errors
from .rubric import rubric
from .three_sixty_review import three_sixty_review
from .functions import functions

# register app
app = Flask(__name__,
            static_url_path='',
            static_folder='static')
app.register_blueprint(errors, flush=True)
app.register_blueprint(rubric, flush=True)
app.register_blueprint(three_sixty_review, flush=True)
app.register_blueprint(functions, flush=True)

app.template_filter('svg2data_url')

# setup logging
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


@app.route("/")
def index():
    """check it's alive"""
    app.logger.debug('DEBUG logging')
    app.logger.info('INFO logging')
    return Response("VirtuousLoop is running!", status=200)


@app.route("/json", methods=["POST"])
def custom():
    """send json and check what is being received"""
    payload = request.get_json()
    return Response(payload, status=200)


@app.route("/health")
def health():
    """check health response"""
    return Response("OK", status=200)