from marshmallow import Schema, fields


class SubmitScoresSchema(Schema):
    scores = fields.Dict(required=True)