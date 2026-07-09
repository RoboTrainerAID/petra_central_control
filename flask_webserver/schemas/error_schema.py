from marshmallow import Schema, fields


class SingleMessageErrorSchema(Schema):
    message = fields.Str()


class ValidationErrorSchema(Schema):
    message = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()))
