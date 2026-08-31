from marshmallow import Schema, fields, validate


class ClinicalScalesSchema(Schema):
    hand_grip_left = fields.Float(
        required=True,
        allow_none=True,
    )
    hand_grip_right = fields.Float(
        required=True,
        allow_none=True,
    )
    ruler_drop = fields.Float(
        required=True,
        allow_none=True,
    )
    jump_and_reach = fields.Float(
        required=True,
        allow_none=True,
    )
    tandem_walk = fields.Float(
        required=True,
        allow_none=True,
    )
    single_leg_stance = fields.Float(
        required=True,
        allow_none=True,
    )
    robotrainer_max_force_front = fields.Float(
        required=True,
        allow_none=True,
    )
    robotrainer_max_force_left = fields.Float(
        required=True,
        allow_none=True,
    )
    robotrainer_max_force_right = fields.Float(
        required=True,
        allow_none=True,
    )