import base64
from typing import Callable

from flask import request
from flask_restful import Resource, abort
from marshmallow import ValidationError

from PIL import Image
from io import BytesIO

from flask_webserver.schemas.robot_map_schema import RobotMapSchema


class RobotMapRelay(Resource):

    storeDict: Callable[[str, dict], None]
    getDict: Callable[[str], dict]

    def __init__(self, storeDict: Callable[[str, dict], None], getDict: Callable[[str], dict]):
        self.storeDict = storeDict
        self.getDict = getDict

    def post(self):
        r = request.get_json(force=True)
        try:
            self.storeDict("rmr", RobotMapSchema().load(r))
        except ValidationError as err:
            abort(400, message=err.messages)
        return RobotMapSchema().dump(self.getDict("rmr"))

    def get(self):
        map_dict = self.getDict("rmr")

        # make default values if map_dict is not present
        if map_dict is None:
            map_dict = {
                'width': 1,
                'height': 1,
                'resolution': 1,
                'origin_x': 0,
                'origin_y': 0,
                'origin_angle': 0
            }

        # convert to image
        image = Image.new('RGBA', (int(map_dict['width']), int(map_dict['height'])))
        # TODO: make colors and stuff
        if 'data' in map_dict.keys():
            ogrid = base64.b64decode(str(map_dict['data']).encode('ascii'))

            def hex2b(hex: str):
                return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4, 6))

            occupied_color = hex2b("263238FF")
            unoccupied_color = hex2b("ECEFF1FF")
            unknown_color = hex2b("81D4FAFF")

            for x in range(image.width):
                for y in range(image.height):
                    occupancy = ogrid[y * image.width + x]
                    image.putpixel((x, y), unknown_color if occupancy < 0 else (occupied_color if occupancy >= 1 else unoccupied_color))

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        image_data = base64.b64encode(buffer.getvalue()).decode('ascii')

        return RobotMapSchema().dump({
            **map_dict,
            'data': image_data
        })
