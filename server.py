import json

import tornado.web
import tornado.gen
import tornado.auth
import tornado.websocket
import motor.motor_tornado
from tornado.web import HTTPError
from tornado.gen import coroutine

from models import init, User, Dialog

motor_client = motor.motor_tornado.MotorClient('localhost', 27017)
db = motor_client['chatdb']
init(db)

