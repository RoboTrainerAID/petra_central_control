from marshmallow import Schema, fields, validates

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.schemas.enums import PayloadType, is_payload_type_valid, is_transport_mode_valid


class PayloadSchema(Schema):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locations_db = None

    def set_locations_db(self, locations_db: MongoDB):
        self.locations_db = locations_db

    _id = fields.Int(dump_only=True)
    type = fields.Int(required=True, validate=is_payload_type_valid)

    name = fields.Str(required=True)
    last_name = fields.Str()
    preferred_mode = fields.Int(validate=is_transport_mode_valid, required=True)
    preferred_language = fields.Str()

    location = fields.Int(required=True)

    @validates("location")
    def validate_location(self, value: int, **kwargs) -> bool:
        return self.locations_db.select_one(value) is not None
