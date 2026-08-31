from marshmallow import Schema, fields


class ParticipantSchema(Schema):
    userId = fields.Str(required=True)