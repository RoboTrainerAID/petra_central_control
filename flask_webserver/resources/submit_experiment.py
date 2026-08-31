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
            description: Submit questionnaire scores for a finished experiment trial and prepare next experiment
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

        # 3. Find associated participant and create the next experiment
        if current_exp and "participant_id" in current_exp:
            raw_p_id = current_exp["participant_id"]

            # Try looking up participant by BSON ObjectId first, then fallback to string
            participant = None
            try:
                participant = participants_collection.find_one({"_id": ObjectId(raw_p_id)})
            except InvalidId:
                pass

            if not participant:
                participant = participants_collection.find_one({"_id": str(raw_p_id)})

            # 4. If participant is not finished, insert the next experiment document
            if participant and not participant.get("is_finished"):
                next_exp_num = participant.get("next_experiment_number", 2)

                new_experiment = {
                    "participant_id": str(participant["_id"]),
                    "status": "waiting",
                    "experiment_number": next_exp_num,
                    "extra_step": False  # Default value; can be updated based on your logic
                }
                self.database.insert(new_experiment)

        return {"message": "Experiment answers successfully recorded."}, 200