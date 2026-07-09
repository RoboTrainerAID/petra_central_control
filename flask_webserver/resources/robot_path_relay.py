from typing import Callable

from flask import request
from flask_restful import Resource, abort
from marshmallow import ValidationError

from flask_webserver.schemas.robot_path_schema import RobotPathSchema


class RobotPathRelay(Resource):

    storeDict: Callable[[str, dict], None]
    getDict: Callable[[str], dict]

    def __init__(self, storeDict: Callable[[str, dict], None], getDict: Callable[[str], dict]):
        self.storeDict = storeDict
        self.getDict = getDict

    def post(self):
        r = request.get_json(force=True)
        try:
            self.storeDict("rpr", RobotPathSchema().load(r))
        except ValidationError as err:
            abort(400, message=err.messages)

        return RobotPathSchema().dump(self.getDict("rpr"))

    def get(self):
        return RobotPathSchema().dump(self.getDict("rpr"))