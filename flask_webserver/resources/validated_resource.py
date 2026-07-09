from flask import request
from flask_restful import Resource, abort
from marshmallow import Schema, ValidationError

from flask_webserver.common.mongo_db import MongoDB


class ValidatedResource(Resource):
    """
    Base class for Resources using a schema to validate their request bodies and responses
    """

    def __init__(self, database: MongoDB):
        """
        Initializes the resource
        :param database: the home database of the resource
        """
        super().__init__()
        self.database = database

    def _schema(self) -> Schema:
        """

        :return: The schema to use to load / dump resource data
        """
        raise NotImplementedError("_schema needs to be implemented by children of ValidatedResource")

    def validate_id(self, resource_id: int):
        """
        Validates the id to be present in locations database
        :param resource_id: the id to validate
        :return: nothing, but aborts if the id is not present
        """
        if self.database.select_one(id=resource_id) is None:
            abort("404", message=f'Could not find id {resource_id} in the database')

    def dump_from_id(self, resource_id: int):
        """
        Dumps the given element from the database
        :param resource_id: the id of the payload to dump
        :return: the resource as to be used in the response by the server
        """
        payload = self.database.select_one(id=resource_id)
        return self._schema().dump(payload)

    def dump_all(self):
        """
        Dumps all elements from the database using the schema given by _schema()
        :return: the resources to use for the response
        """
        payloads = self.database.select_all()
        return self._schema().dump(payloads, many=True)

    def load_from_request(self, allow_patch: bool = False):
        """
        Loads the resource from the request body and validates it using the schema given by _schema()
        :return: the resource ready to be used for processing
        """
        try:
            r = request.get_json(force=True)
            print(r)
            return self._schema().load(r, partial=allow_patch)
        except ValidationError as err:
            print(err.messages)
            abort(400, message=err.messages)
