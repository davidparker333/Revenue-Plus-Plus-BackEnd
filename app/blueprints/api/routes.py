from . import bp as api
from app import db

@api.route('/')
def hello_world():
    return "Hello World"