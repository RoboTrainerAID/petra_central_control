from marshmallow import Schema, fields


class IFISSchema(Schema):
    """Schema for validating International Fitness Scale (IFIS) answers."""

    ifis = fields.Dict(
        keys=fields.Str(),
        values=fields.Int(),
        required=True,
    )