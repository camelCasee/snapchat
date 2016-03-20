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


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_cookie('name')


class MainHandler(BaseHandler):
    def get(self):
        # if not self.get_current_user():
        #     self.redirect('/loginpage')
        f = open('static/chats/chats.html')
        s = f.read()
        f.close()
        self.write(s)


class LoginHandler(BaseHandler):
    @coroutine
    def post(self):
        try:
            data = json.loads(self.request.body.decode())
            username = data['name']
            password = data['password']
        except:
            raise
        res = yield User.check(username, password)
        if res:
            self.set_cookie('name', username, expires_days=7)


class LoginPageHandler(BaseHandler):
    def get(self):
        f = open('static/login/login.html')
        s = f.read()
        f.close()
        self.write(s)


class UserHandler(BaseHandler):
    @coroutine
    def get(self, name):
        user = yield User.load(name)
        if user:
            user = User.public_dict(user)
            self.write(user)
        else:
            raise HTTPError(400, 'user doesnt exist')


class ChangeUserHandler(BaseHandler):
    @coroutine
    def post(self):
        try:
            data = json.loads(self.request.body.decode())
        except:
            raise

        action = data['action']
        user_data = data['user']
        if action == 'create':
            if User.validate(user_data):
                saved = yield User.save(user_data)
                if saved:
                    self.write('success')
                    return
            raise HTTPError(400, 'bad input')
        elif action == 'update':
            pass


class DialogHandler(BaseHandler):
    @coroutine
    def post(self):
        try:
            data = json.loads(self.request.body.decode())
        except:
            raise
        name = data['name']
        people = data['people']
        res = yield Dialog.create(people, name)
        if res:
            self.write('ok')
        else:
            raise HTTPError(400, 'hz')

    @coroutine
    def get(self):
        """ :returns all dialogs of current_user """
        user = self.get_current_user()
        if not user:
            raise HTTPError(300, 'forbidden')
        res = yield Dialog.get_all_with_user(user)
        self.write(json.dumps(res))


class Application(tornado.web.Application):
    def __init__(self):
        self.webSocketsPool = []

        settings = {
            'static_url_prefix': 'static/',
        }

        handlers = (
            (r'/', MainHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler,
            {'path': 'static/'}),
            (r'/users/(\w*)', UserHandler),
            (r'/users', ChangeUserHandler),
            (r'/login', LoginHandler),
            (r'/dialogs', DialogHandler),
            (r'/websocket/?', WebSocket),
            (r'/loginpage', LoginPageHandler),
            (r'/chats', MainHandler),
        )

        tornado.web.Application.__init__(self, handlers, **settings)
