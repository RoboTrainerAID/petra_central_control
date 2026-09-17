from marshmallow import Schema
from bson.objectid import ObjectId
from bson.errors import InvalidId

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.resources.validated_resource import ValidatedResource
from flask_webserver.schemas.new_experiment_schema import NewExperimentSchema


class NewExperiment(ValidatedResource):

    def __init__(self, experiments_db: MongoDB, participants_db: MongoDB):
        super().__init__(database=experiments_db)
        self.participants_db = participants_db

    def _schema(self) -> Schema:
        return NewExperimentSchema()

    def post(self, participant_id: str):
        ''' ---
            description: Create a new experiment for a participant
            tags:
              - experiment
            parameters:
              - in: path
                name: participant_id
                description: ID of the partiscipant for whom the new experiment is being created
                required: true
                schema:
                    type: string
            requestBody:
                description: Parameters for the new experiment
                required: true
                content:
                    application/json:
                        schema: NewExperimentSchema
            responses:
                200:
                    description: New experiment created successfully
                400:
                    description: Invalid request parameters
                404:
                    description: Participant not found
        '''
        json_data = self.load_from_request()

        experiment_collection = getattr(self.database, 'collection', getattr(self.database, 'table', None))
        participants_collection = getattr(self.participants_db, 'collection', getattr(self.participants_db, 'table', None))

        # Check if the participant exists
        participant = None
        try:
            participant = participants_collection.find_one({"_id": ObjectId(participant_id)})
        except InvalidId:
            pass

        if not participant:
            return {"message": f"Participant with ID '{participant_id}' not found."}, 404

        new_experiment = {
            "participant_id": str(participant["_id"]),
        }
        new_experiment.update(json_data)
        self.database.insert(new_experiment)

        return {"message": "Experiment answers successfully recorded."}, 200