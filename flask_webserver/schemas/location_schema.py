from marshmallow import Schema, fields

from flask_webserver.schemas.enums import is_location_type_valid


class LocationSchema(Schema):

    _id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    floor = fields.Int(required=True)
    type = fields.Int(required=True, validate=is_location_type_valid)
    position_x = fields.Float(required=True)
    position_y = fields.Float(required=True)
    quaternion_x = fields.Float(required=True)
    quaternion_y = fields.Float(required=True)
    quaternion_z = fields.Float(required=True)
    quaternion_w = fields.Float(required=True)
