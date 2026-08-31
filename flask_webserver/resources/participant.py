from flask import request
from marshmallow import Schema

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.resources.validated_resource import ValidatedResource
from flask_webserver.schemas.participant_schema import ParticipantSchema


class Participant(ValidatedResource):

    def __init__(self, participants_db: MongoDB, experiments_db: MongoDB):
        super().__init__(database=participants_db)
        self.experiments_db = experiments_db

    def _schema(self) -> Schema:
        return ParticipantSchema()

    def post(self):
        ''' ---
            description: Register a new participant in the database and create initial experiment
            tags:
              - experiment
            requestBody:
                description: Participant details
                required: true
                content:
                    application/json:
                        schema: ParticipantSchema
            responses:
                201:
                    description: Participant registered successfully and first experiment created
                    content:
                        application/json:
                            schema:
                                type: object
                                properties:
                                    participant_db_id:
                                        type: string
                400:
                    description: Missing or invalid JSON parameters
                    content:
                        application/json:
                            schema: ValidationErrorSchema
        '''
        json_data = self.load_from_request()
        
        # 1. Insert participant into database
        result = self.database.insert(json_data)
        inserted_id = getattr(result, 'inserted_id', result)
        participant_db_id = str(inserted_id)

        # 2. Create the first experiment associated with this participant
        first_experiment = {
            "participant_id": participant_db_id,
            "status": "waiting",
            "experiment_number": 1,
            "extra_step": False  # Default value; can be updated based on your logic
        }
        self.experiments_db.insert(first_experiment)

        self.database.update(
            id=inserted_id,
            data={"next_experiment_number": 2,
                  "is_finished": False}
        )

        return {"participant_db_id": participant_db_id}, 201