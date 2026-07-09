from marshmallow import Schema

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.resources.validated_resource import ValidatedResource
from flask_webserver.schemas.location_schema import LocationSchema


class Location(ValidatedResource):

    def __init__(self, locations_db: MongoDB):
        super().__init__(database=locations_db)

    def _schema(self) -> Schema:
        return LocationSchema()

    def get(self, location_id):
        ''' ---
            description: get a single location
            tags:
              - location
            parameters:
              - in: path
                name: location_id
                description: ID of location to return
                required: true
                schema:
                    type: integer
            responses:
                200:
                    description: location returned successfully
                    content:
                        application/json:
                            schema: LocationSchema
                404:
                    description: location id doesn't exist
                    content:
                        application/json:
                            schema: SingleMessageErrorSchema
        '''
        self.validate_id(location_id)
        return self.dump_from_id(location_id), 200

    def put(self, location_id):
        ''' ---
            description: modify an existing location
            tags:
              - location
            parameters:
              - in: path
                name: location_id
                description: unique_location to modify
                required: true
                schema:
                    type: string
            requestBody:
                description: location object to update
                required: true
                content:
                    application/json:
                        schema: LocationSchema
            responses:
                200:
                    description: location modified successfully
                    content:
                        application/json:
                            schema: LocationSchema
                404:
                    description: location id doesn't exist
                    content:
                        application/json:
                            schema: SingleMessageErrorSchema
                400:
                    description: missing json input parameter
                    content:
                        application/json:
                            schema: ValidationErrorSchema
        '''
        self.validate_id(location_id)
        json_data = self.load_from_request()
        json_data["_id"] = location_id
        self.database.update(id=location_id, data=json_data)

        return self.dump_from_id(location_id), 200

    def delete(self, location_id):
        ''' ---
            description: delete specific location
            tags:
              - location
            parameters:
              - in: path
                name: location_id
                description: unique_location to delete
                required: true
                schema:
                    type: string
            responses:
                200:
                    description: location deleted successfully
                    content:
                        application/json:
                            schema:
                                type: array
                                items: LocationSchema
        '''
        self.database.delete_one(id=location_id)

        return {}, 200
