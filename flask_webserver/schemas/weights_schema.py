from marshmallow import Schema, fields


class WeightsSchema(Schema):
    """Schema for validating pairwise category comparison weights."""

    weights = fields.Dict(
        keys=fields.Str(),
        values=fields.Int(),
        required=True,
        metadata={"description": "Dictionary of NASA-TLX category weights summing to 15"}
    )