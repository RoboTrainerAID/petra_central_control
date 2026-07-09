from typing import Callable

from flask import request
from flask_restful import Resource, abort
from marshmallow import ValidationError

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.resources.validated_resource import ValidatedResource
from flask_webserver.schemas.robot_position_schema import RobotPositionSchema


class RobotPositionRelay(Resource):

    storeDict: Callable[[str, dict], None]
    getDict: Callable[[str], dict]

    def __init__(self, storeDict: Callable[[str, dict], None], getDict: Callable[[str], dict]):
        self.storeDict = storeDict
        self.getDict = getDict

    def post(self):
        r = request.get_json(force=True)
        try:
            self.storeDict("rposr", RobotPositionSchema().load(r))
        except ValidationError as err:
            abort(400, message=err.messages)
        return RobotPositionSchema().dump(self.getDict("rposr"))

    def get(self):
        return RobotPositionSchema().dump(self.getDict("rposr"))
