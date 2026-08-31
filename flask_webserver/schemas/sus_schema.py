from marshmallow import Schema, fields, validate


class SusSchema(Schema):
    """Schema for validating System Usability Scale (SUS) 10-item responses."""

    q1 = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    q2 = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    q3 = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    q4 = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    q5 = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    q6 = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    q7 = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    q8 = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    q9 = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    q10 = fields.Int(required=True, validate=validate.Range(min=1, max=5))
