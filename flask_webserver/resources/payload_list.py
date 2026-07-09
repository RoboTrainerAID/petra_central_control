from flask import request
from marshmallow import Schema

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.resources.validated_resource import ValidatedResource
from flask_webserver.schemas.payload_schema import PayloadSchema


class PayloadList(ValidatedResource):

    def __init__(self, payloads_db: MongoDB, locations_db: MongoDB):
        super().__init__(payloads_db)
        self.locations_db = locations_db

    def _schema(self) -> Schema:
        schema = PayloadSchema()
        schema.set_locations_db(self.locations_db)
        return schema

    def get(self):
        """
        Retrieves all payloads from the database
        :return: the payloads fetched from the database
        ---
            description: retrieves all payloads from the database
            tags:
              - payload
            responses:
                200:
                    description: database was reached
                    content:
                        application/json:
                            type: array
                            items: PayloadSchema
        """
        return self.dump_all(), 200

    def post(self):
        """
        Creates a new payload with the given data
        :return: the data of the new payload as stored in the database
        ---
            description: creates a new payload
            tags:
              - payload
            requestBody:
                description: data to save for the new payload
                required: true
                content:
                    application/json:
                        schema: PayloadSchema
            responses:
                201:
                    description: new payload was created successfully
                    content:
                        application/json:
                            schema: PayloadSchema
                400:
                    description: failed to validated request body
                    content:
                        application/json:
                            schema: ValidationErrorSchema
                    
        """
        json_data = request.get_json(force=True)

        new_id = self.database.get_highest_id() + 1
        json_data["_id"] = new_id

        self.database.insert(json_data)
        return self.dump_from_id(resource_id=new_id), 201

    def delete(self):
        """
        Deletes all Payloads from the database
        :return: am empty list
        ---
            description: deletes all payloads from the database
            tags:
              - payload
            responses:
                200:
                    description: payloads have been successfully deleted
                    content:
                        application/json:
                            schema:
                                type: array
                                items: PayloadSchema
        """
        self.database.delete_all()
        return [], 200
