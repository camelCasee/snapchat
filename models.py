from tornado.gen import coroutine
import hashlib
md5 = hashlib.md5()


def init(db):
    User.db = db
    Dialog.db = db


class User:
    db = None
    required = ['name', 'password']

    @classmethod
    def validate(cls, data: dict):
        if not isinstance(data, dict):
            return False
        for foo in cls.required:
            if foo not in data.keys():
                return False
        return True

    @classmethod
    @coroutine
    def check(cls, username, password):
        md5.update(password.encode())
        password = md5.digest()
        user = yield cls.db.users.find_one({'name': username})
        if user and user['password'] == password:
            return True
        else:
            return False

    @classmethod
    @coroutine
    def save(cls, data: dict):
        future = yield cls.db.users.find_one({'name': data['name']})
        if not future:
            md5.update(data['password'].encode())
            data['password'] = md5.digest()
            yield cls.db.users.insert(data)
            return True
        return False

    @classmethod
    def public_dict(cls, data: dict):
        data = data.copy()
        if 'password' in data.keys():
            del data['password']
            del data['_id']
        return data

    @classmethod
    @coroutine
    def load(cls, name):
        user = yield cls.db.users.find_one({'name': name})
        if user:
            return user
        return None
