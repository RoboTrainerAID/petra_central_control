from flask import request
from flask_restful import Resource, abort
from marshmallow import Schema

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.common.authentication import Authentication
from flask_webserver.resources.validated_resource import ValidatedResource
from flask_webserver.schemas.user_schema import UserSchema


class User(ValidatedResource):

    def __init__(self, users_db: MongoDB):
        super().__init__(database=users_db)

    def _schema(self) -> Schema:
        return UserSchema()

    def get(self, user_id):
        ''' ---
            description: get a single user
            tags:
              - user
            parameters:
              - in: path
                name: user_id
                description: ID of user to return
                required: true
                schema:
                    type: integer
            responses:
                200:
                    description: user returned successfully
                    content:
                        application/json:
                            schema: UserSchema
                404:
                    description: user id doesn't exist
                    content:
                        application/json:
                            schema: SingleMessageErrorSchema
        '''
        return self.dump_from_id(user_id), 200

    def put(self, user_id):
        ''' ---
            description: modify an existing user
            tags:
              - user
            parameters:
              - in: path
                name: user_id
                description: id of the user to modify
                required: true
                schema:
                    type: integer
            requestBody:
                description: User object to create
                required: true
                content:
                    application/json:
                        schema: UserSchema
            responses:
                200:
                    description: user modified successfully
                    content:
                        application/json:
                            schema: UserSchema
                404:
                    description: user id doesn't exist
                    content:
                        application/json:
                            schema: SingleMessageErrorSchema
                400:
                    description: missing json input parameter
                    content:
                        application/json:
                            schema: ValidationErrorSchema
        '''
        json_data = self.load_from_request()
        json_data["_id"] = user_id

        # hash password
        json_data["password_hash"] = Authentication.hash_password(json_data["password"])
        del json_data["password"]

        self.database.update(id=user_id, data=json_data)

        return self.dump_from_id(user_id), 200

    def delete(self, username):
        ''' ---
            description: delete specific user
            tags:
              - user
            parameters:
              - in: path
                name: username
                description: id of the user to delete
                required: true
                schema:
                    type: integer
            responses:
                200:
                    description: user deleted successfully
                    content:
                        application/json:
                            schema: UserSchema
        '''
        self.database.delete_one(id=username)

        return {}, 200
