from marshmallow import Schema, fields


class RobotPositionSchema(Schema):
    x = fields.Float(required=True)
    y = fields.Float(required=True)
    angle = fields.Float(required=True)
