from marshmallow import Schema, fields


class NewExperimentSchema(Schema):
    status = fields.String(required=True)
    experiment_name = fields.String(required=True)
    extra_step = fields.Boolean(required=True)
    force = fields.Integer(required=True)
    type = fields.String(required=True)
    method = fields.String(required=True)
    flag = fields.String(required=True)
    details = fields.Dict(required=True)
    scenario_id = fields.String(required=True)