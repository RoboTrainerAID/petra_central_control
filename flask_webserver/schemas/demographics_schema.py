from marshmallow import Schema, fields


class DemographicsSchema(Schema):
    """Schema for validating participant demographic data."""

    age = fields.Int(required=True, allow_none=True)
    gender = fields.Str(required=True, allow_none=True)
    experience_level = fields.Str(required=False, allow_none=True)