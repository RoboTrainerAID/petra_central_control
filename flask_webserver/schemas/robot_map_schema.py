from marshmallow import Schema, fields


class RobotMapSchema(Schema):

    data = fields.Raw(required=True)

    resolution = fields.Number(required=True, default=0)
    width = fields.Number(required=True, default=1)
    height = fields.Number(required=True, default=1)
    origin_x = fields.Number(required=True, default=0)
    origin_y = fields.Number(required=True, default=0)
    origin_angle = fields.Number(required=True, default=0)
