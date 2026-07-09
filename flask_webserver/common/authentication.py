from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.common.sqlite_db import SqliteDB
from passlib.apps import custom_app_context as pwd_context

# db = SqliteDB(table="users")
db = MongoDB(table="users")


class Authentication:

    def login(username, password):
        user = db.select_filtered({"username": username})[0]
        if user is None:
            return {"message": "User {} doesn't exist".format(username)}, 401

        if Authentication.verify_password(password, user['password_hash']):
            return {"message": "Login successful"}, 200

        else:
            return {"message": "Wrong password for {}".format(username)}, 401

    def logout():
        return {"message": "Logout successful"}, 200

    def hash_password(password: str) -> str:
        return pwd_context.encrypt(password)

    def verify_password(password: str, password_hash: str) -> bool:
        return pwd_context.verify(password, password_hash)
