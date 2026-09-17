from marshmallow import Schema, fields



class ChangeExperimentStatusSchema(Schema):
    status = fields.String(required=True)