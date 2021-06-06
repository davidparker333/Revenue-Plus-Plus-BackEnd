from . import bp as auth
from app import db

@auth.route('/')
def hello_world():
    return "Hello World"