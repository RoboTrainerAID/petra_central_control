from marshmallow import Schema

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.resources.validated_resource import ValidatedResource
from flask_webserver.schemas.transport_schema import TransportSchema


class TransportList(ValidatedResource):

    def __init__(self, transports_db: MongoDB, locations_db: MongoDB, payloads_db: MongoDB):
        super().__init__(database=transports_db)
        self.locations_db = locations_db
        self.payloads_db = payloads_db

    def _schema(self) -> Schema:
        schema = TransportSchema()
        schema.set_databases(self.payloads_db, self.locations_db)
        return schema

    def get(self):
        ''' ---
            description: gives list of all transports
            tags:
              - transport
            responses:
                200:
                    description: list with at least one entry found
                    content:
                        application/json:
                            schema:
                                type: array
                                items: TransportSchema
        '''
        return self.dump_all(), 200

    def post(self):
        ''' ---
            description: create a new transport
            tags:
              - transport
            requestBody:
                description: Transport object to create
                required: true
                content:
                    application/json:
                        schema: TransportSchema
            responses:
                201:
                    description: Transport created successfully
                    content:
                        application/json:
                            schema: TransportSchema
                400:
                    description: missing json input parameter or location doesn't exist
                    content:
                        application/json:
                            schema: ValidationErrorSchema
        '''
        json_data = self.load_from_request()
        new_id = self.database.get_highest_id() + 1
        json_data["_id"] = new_id
        self.database.insert(data=json_data)

        return self.dump_from_id(new_id), 201

    def delete(self):
        ''' ---
            description: delete all entries in the list
            tags:
              - transport
            responses:
                200:
                    description: all entries deleted successfully
                    content:
                        application/json:
                            schema:
                                type: array
                                items: TransportSchema
        '''
        self.database.delete_all()

        return [], 200
