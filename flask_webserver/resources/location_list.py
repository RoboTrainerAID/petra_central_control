from marshmallow import Schema

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.resources.validated_resource import ValidatedResource
from flask_webserver.schemas.location_schema import LocationSchema


class LocationList(ValidatedResource):

    def __init__(self, locations_db: MongoDB):
        super().__init__(database=locations_db)

    def _schema(self) -> Schema:
        return LocationSchema()

    def get(self):
        ''' ---
            description: gives list of all locations
            tags:
              - location
            responses:
                200:
                    description: list with at least one entry found
                    content:
                        application/json:
                            schema: 
                                type: array
                                items: LocationSchema
        '''
        return self.dump_all(), 200

    def post(self):
        ''' ---
            description: create a new location
            tags:
              - location
            requestBody:
                description: location object to create
                required: true
                content:
                    application/json:
                        schema: LocationSchema
            responses:
                201:
                    description: location created successfully
                    content:
                        application/json:
                            schema: LocationSchema
                400:
                    description: location name+floor already in use or missing json parameter
                    content:
                        application/json:
                            schema: ValidationErrorSchema
        '''
        json_data = self.load_from_request()
        new_id = self.database.get_highest_id() + 1
        json_data['_id'] = new_id
        self.database.insert(data=json_data)

        return self.dump_from_id(new_id), 201

    def delete(self):
        ''' ---
            description: delete all entries in the list
            tags:
              - location
            responses:
                200:
                    description: all entries deleted successfully
                    content:
                        application/json:
                            schema:
                                type: array
                                items: LocationSchema
        '''
        self.database.delete_all()

        return [], 200
