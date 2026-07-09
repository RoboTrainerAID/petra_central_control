from marshmallow import Schema, fields


class RobotPathNode(Schema):
    x = fields.Float(required=True)
    y = fields.Float(required=True)
    angle = fields.Float(required=True)


class RobotPathSchema(Schema):
    nodes = fields.List(fields.Nested(RobotPathNode), required=True, default=[])
