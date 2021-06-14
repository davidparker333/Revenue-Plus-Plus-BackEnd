from . import bp as api
from app import db
from flask import request, jsonify, json

@api.route('/')
def hello_world():
    a = {"text": "Hello World"}
    return jsonify(a)