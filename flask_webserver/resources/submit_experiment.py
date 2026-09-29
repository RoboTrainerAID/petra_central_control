from marshmallow import Schema
from bson.objectid import ObjectId
from bson.errors import InvalidId

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.resources.validated_resource import ValidatedResource
from flask_webserver.schemas.submit_scores_schema import SubmitScoresSchema


class SubmitExperiment(ValidatedResource):

    def __init__(self, experiments_db: MongoDB, participants_db: MongoDB):
        super().__init__(database=experiments_db)
        self.participants_db = participants_db

    def _schema(self) -> Schema:
        return SubmitScoresSchema()

    def post(self, experiment_id: str):
        ''' ---
            description: Submit questionnaire scores for a finished experiment trial
            tags:
              - experiment
            parameters:
              - in: path
                name: experiment_id
                description: ID of the active experiment being submitted
                required: true
                schema:
                    type: string
            requestBody:
                description: Scores dictionary payload
                required: true
                content:
                    application/json:
                        schema: SubmitScoresSchema
            responses:
                200:
                    description: Experiment scores recorded successfully
                400:
                    description: Invalid request payload
        '''
        json_data = self.load_from_request()
        scores = json_data.get("scores", {})

        experiment_collection = getattr(self.database, 'collection', getattr(self.database, 'table', None))
        participants_collection = getattr(self.participants_db, 'collection', getattr(self.participants_db, 'table', None))

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

        # 2. Update status of the current experiment to completed
        self.database.update(
            id=target_exp_id,
            data={
                "scores": scores,
                "status": "completed"
            }
        )

        return {"message": "Experiment answers successfully recorded."}, 200