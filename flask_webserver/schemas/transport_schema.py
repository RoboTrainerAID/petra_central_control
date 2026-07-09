from marshmallow import Schema, fields, validates

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.schemas.enums import is_transport_mode_valid, is_transport_status_valid

TRANSPORT_STATUS_WAITING = 0
TRANSPORT_STATUS_RUNNING = 1
TRANSPORT_STATUS_DONE = 2


class TransportSchema(Schema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locations_db: MongoDB | None = None
        self.payloads_db: MongoDB | None = None

    def set_databases(self, payloads_db: MongoDB, locations_db: MongoDB):
        self.payloads_db = payloads_db
        self.locations_db = locations_db

    _id = fields.Int(dump_only=True)  # ids in requests are given through url
    status = fields.Int(validate=is_transport_status_valid, required=True)

    payload = fields.Int(required=True)

    @validates("payload")
    def validate_payload(self, value: int) -> bool:
        return self.payloads_db.select_one(value) is not None

    override_mode = fields.Int(validate=is_transport_mode_valid, required=False, allow_none=True)
    override_start_location = fields.Int(required=False, allow_none=True)

    @validates("override_start_location")
    def validate_start_location(self, value: int) -> bool:
        return self.locations_db.select_one(value) is not None

    goal_location = fields.Int(required=True)

    @validates("goal_location")
    def validate_goal_location(self, value: int) -> bool:
        return self.locations_db.select_one(value) is not None

    time_stamp = fields.Int(required=True)
    is_start_time = fields.Bool(required=True)

    platform_nr = fields.Int(required=True, default=-1)
    duration = fields.Float(dump_only=True, default=30)
