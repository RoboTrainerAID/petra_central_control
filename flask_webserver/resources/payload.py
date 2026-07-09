from marshmallow import Schema

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.resources.validated_resource import ValidatedResource
from flask_webserver.schemas.payload_schema import PayloadSchema


class Payload(ValidatedResource):

    def __init__(self, payloads_db: MongoDB, locations_db: MongoDB):
        super().__init__(payloads_db)
        self.locations_db = locations_db

    def _schema(self) -> Schema:
        schema = PayloadSchema()
        schema.set_locations_db(self.locations_db)
        return schema

    def get(self, payload_id):
        """
        Retrieves a single payload
        :param payload_id: the id of the payload to retrieve
        :return: the payload itself
        ---
            description: get a single payload
            tags:
              - payload
            parameters:
                - in: path
                  name: payload_id
                  description: ID of payload to return
                  required: true
                  schema:
                      type: integer
            responses:
                200:
                    description: payload was found in database
                    content:
                        application/json:
                            schema: PayloadSchema
                404:
                    description: payload id was not found in database
                    content:
                        application/json:
                            schema: SingleMessageErrorSchema
        """
        self.validate_id(payload_id)
        return self.dump_from_id(payload_id), 200

    def put(self, payload_id):
        """
        Replaces a single payload
        :param payload_id: the id of the payload that should be replaced
        :return: the new data from the database
        ---
            description: replaces a single payload
            tags:
                - payload
            parameters:
                - in: path
                  name: payload_id
                  description: ID of payload to return
                  required: true
                  schema:
                      type: integer
            requestBody:
                description: data to use as a replacement
                required: true
                content:
                    application/json:
                        schema: PayloadSchema
            responses:
                200:
                    description: payload was successfully replaced
                    content:
                        application/json:
                            schema: PayloadSchema
                404:
                    description: payload id was not found in database
                    content:
                        application/json:
                            schema: SingleMessageErrorSchema
                400:
                    description: request body could not be validated
                    content:
                        application/json:
                            schema: ValidationErrorSchema
        """
        self.validate_id(payload_id)
        json_data = self.load_from_request()
        json_data["_id"] = payload_id
        self.database.update(payload_id, json_data)

        return self.dump_from_id(payload_id), 200

    def patch(self, payload_id):
        """
        Replaces only part of an existing payload
        :param payload_id: the id of the payload to patch
        :return: the patched payload data
        ---
            description: patches a single payload
            tags:
                - payload
            parameters:
                - in: path
                  name: payload_id
                  description: ID of payload to return
                  required: true
                  schema:
                      type: integer
            requestBody:
                description: fields to update
                required: true
                content:
                    application/json:
                        schema: PayloadSchema
            responses:
                200:
                    description: payload was successfully patched
                    content:
                        application/json:
                            schema: PayloadSchema
                404:
                    description: payload id was not found in database
                    content:
                        application/json:
                            schema: SingleMessageErrorSchema
                400:
                    description: request body could not be validated
                    content:
                        application/json:
                            schema: ValidationErrorSchema
        """
        self.validate_id(payload_id)
        json_data = self.load_from_request()
        json_data["_id"] = payload_id
        self.database.update(payload_id, json_data)

        return self.dump_from_id(payload_id), 200

    def delete(self, payload_id):
        """
        Deletes a single payload from the database
        :param payload_id: the id of the payload to delete
        :return: an empty object to signal the payload has been deleted
        ---
            description: deletes a single payload
            tags:
              - payload
            parameters:
                - in: path
                  name: payload_id
                  description: ID of payload to return
                  required: true
                  schema:
                      type: integer
            responses:
                200:
                    description: payload was successfully deleted
                    content:
                        application/json:
                            schema:
                                type: object
                404:
                    description: payload id was not found in database
                    content:
                        application/json:
                            schema: SingleMessageErrorSchema
        """
        self.validate_id(payload_id)
        self.database.delete_one(payload_id)
        return {}, 200
