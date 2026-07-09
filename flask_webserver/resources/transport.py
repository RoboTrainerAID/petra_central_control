from flask import request
from flask_restful import Resource, abort
from marshmallow import Schema

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.resources.validated_resource import ValidatedResource
from flask_webserver.schemas.transport_schema import TransportSchema


class Transport(ValidatedResource):

    def __init__(self, transports_db: MongoDB, locations_db: MongoDB, payloads_db: MongoDB):
        super().__init__(database=transports_db)
        self.locations_db = locations_db
        self.payloads_db = payloads_db

    def _schema(self) -> Schema:
        schema = TransportSchema()
        schema.set_databases(self.payloads_db, self.locations_db)
        return schema

    def get(self, transport_id):
        ''' ---
            description: get a single transport
            tags:
              - transport
            parameters:
              - in: path
                name: transport_id
                description: ID of Transport to return
                required: true
                schema:
                    type: integer
            responses:
                200:
                    description: Transport returned successfully
                    content:
                        application/json:
                            schema: TransportSchema
                404:
                    description: Transport id doesn't exist
                    content:
                        application/json:
                            schema: SingleMessageErrorSchema
        '''
        return self.dump_from_id(transport_id), 200

    def put(self, transport_id):
        ''' ---
            description: modify an existing transport
            tags:
              - transport
            parameters:
              - in: path
                name: transport_id
                description: ID of Transport to modify
                required: true
                schema:
                    type: integer
            requestBody:
                description: Transport object to update
                required: true
                content:
                    application/json:
                        schema: TransportSchema
            responses:
                200:
                    description: Transport modified successfully
                    content:
                        application/json:
                            schema: TransportSchema
                404:
                    description: Transport id doesn't exist
                    content:
                        application/json:
                            schema: SingleMessageErrorSchema
                400:
                    description: missing json input parameter or location doesn't exist
                    content:
                        application/json:
                            schema: ValidationErrorSchema
        '''
        json_data = self.load_from_request()
        json_data["_id"] = transport_id
        self.database.update(id=transport_id, data=json_data)

        return self.dump_from_id(transport_id), 200

    def patch(self, transport_id):
        ''' ---
            description: modify an existing transport with incomplete data
            tags:
              - transport
            parameters:
              - in: path
                name: transport_id
                description: ID of Transport to modify
                required: true
                schema:
                    type: integer
            requestBody:
                description: Data to update
                required: true
                content:
                    application/json:
                        schema: TransportSchema
            responses:
                200:
                    description: Transport modified successfully
                    content:
                        application/json:
                            schema: TransportSchema
                404:
                    description: Transport id doesn't exist
                    content:
                        application/json:
                            schema: SingleMessageErrorSchema
        '''
        json_data = self.load_from_request(allow_patch=True)
        json_data["_id"] = transport_id
        self.database.update(id=transport_id, data=json_data)

        return self.dump_from_id(transport_id), 200

    def delete(self, transport_id):
        ''' ---
            description: delete specific transport
            tags:
              - transport
            parameters:
              - in: path
                name: transport_id
                description: ID of Transport to delete
                required: true
                schema:
                    type: integer
            responses:
                200:
                    description: Transport deleted successfully
                    content:
                        application/json:
                            schema: TransportSchema
        '''
        self.database.delete_one(id=transport_id)

        return {}, 200
