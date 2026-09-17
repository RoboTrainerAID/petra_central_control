from marshmallow import Schema
from bson.objectid import ObjectId
from bson.errors import InvalidId

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.resources.validated_resource import ValidatedResource
from flask_webserver.schemas.change_experiment_status_schema import ChangeExperimentStatusSchema


class ChangeExperimentStatus(ValidatedResource):

    def __init__(self, experiments_db: MongoDB):
        super().__init__(database=experiments_db)

    def _schema(self) -> Schema:
        return ChangeExperimentStatusSchema()

    def post(self, experiment_id: str):
        ''' ---
            description: CHange the status of an experiment
            tags:
              - experiment
            parameters:
              - in: path
                name: experiment_id
                description: ID of the experiment
                required: true
                schema:
                    type: string
            requestBody:
                description: New status
                required: true
                content:
                    application/json:
                        schema: ChangeExperimentStatusSchema
            responses:
                200:
                    description: Experiment status updated successfully
                400:
                    description: Invalid request payload
                404:
                    description: Experiment not found
        '''
        json_data = self.load_from_request()
        status = json_data.get("status")

        experiment_collection = getattr(self.database, 'collection', getattr(self.database, 'table', None))

        # 1. Fetch current experiment document (trying both ObjectId and string _id)
        current_exp = None
        target_exp_id = experiment_id

        try:
            target_exp_id = ObjectId(experiment_id)
            current_exp = experiment_collection.find_one({"_id": target_exp_id})
        except InvalidId:
            pass

        if not current_exp:
            target_exp_id = experiment_id
            current_exp = experiment_collection.find_one({"_id": target_exp_id})

        if not current_exp:
            return {"message": f"Experiment with ID '{experiment_id}' not found."}, 404

        # 2. Update status of the current experiment to completed
        self.database.update(
            id=target_exp_id,
            data={
                "status": status
            }
        )

        return {"message": "Experiment status updated successfully."}, 200