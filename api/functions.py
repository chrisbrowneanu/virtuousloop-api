from flask import Blueprint
import os

functions = Blueprint("functions", __name__)


def template_path():
    base = os.getcwd()
    path = os.path.join(base, "jinja", "templates")
    return path


def stylesheet_path(stylesheet):
    base = os.getcwd()
    path = os.path.join(base, "static", "css", stylesheet)
    return path

