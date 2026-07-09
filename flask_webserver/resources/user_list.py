from flask import request
from flask_restful import Resource, abort
from marshmallow import Schema

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.common.sqlite_db import SqliteDB
from flask_webserver.common.authentication import Authentication
from flask_webserver.resources.validated_resource import ValidatedResource
from flask_webserver.schemas.user_schema import UserSchema


class UserList(ValidatedResource):

    def __init__(self, users_db: MongoDB):
        super().__init__(database=users_db)

    def _schema(self) -> Schema:
        return UserSchema()

    def get(self):
        ''' ---
            description: gives list of all users
            tags:
              - user
            responses:
                200:
                    description: list with at least one entry found
                    content:
                        application/json:
                            schema: UserSchema
        '''
        return self.dump_all(), 200

    def post(self):
        ''' ---
            description: create a new user
            tags:
              - user
            requestBody:
                description: User object to create
                required: true
                content:
                    application/json:
                        schema: UserSchema
            responses:
                201:
                    description: user created successfully
                    content:
                        application/json:
                            schema: UserSchema
                400:
                    description: user id already exist or missing json input parameter
                    content:
                        application/json:
                            schema: ValidationErrorSchema
        '''
        json_data = self.load_from_request()
        json_data["password_hash"] = Authentication.hash_password(json_data['password'])
        del json_data["password"]

        new_id = self.database.get_highest_id() + 1
        json_data["_id"] = new_id
        self.database.insert(data=json_data)

        return self.dump_from_id(new_id), 201

    def delete(self):
        ''' ---
            description: delete all entries in the list
            tags:
              - user
            responses:
                200:
                    description: all entries deleted successfully
                    content:
                        application/json:
                            schema:
                                type: array
                                items: UserSchema
        '''
        self.database.delete_all()

        return [], 200
