from marshmallow import Schema
from bson.objectid import ObjectId
from bson.errors import InvalidId

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.resources.validated_resource import ValidatedResource


class Experiment(ValidatedResource):

    def __init__(self, experiments_db: MongoDB):
        super().__init__(database=experiments_db)

    def _schema(self) -> Schema:
        # GET request does not validate a request body schema
        return None

    def get(self, experiment_id: str = None):
        ''' ---
            description: Retrieve details of a specific experiment by ID
            tags:
              - experiment
            parameters:
              - in: path
                name: experiment_id
                description: ID of the experiment to retrieve
                required: true
                schema:
                    type: string
            responses:
                200:
                    description: Experiment details retrieved successfully
                404:
                    description: Experiment not found
        '''
        target_id = experiment_id

        experiments_collection = getattr(
            self.database, 'collection', getattr(self.database, 'table', None)
        )

        # 1. Resolve experiment by ID (trying both ObjectId and raw string)
        experiment = None
        try:
            experiment = experiments_collection.find_one({"_id": ObjectId(target_id)})
        except InvalidId:
            pass

        if not experiment:
            experiment = experiments_collection.find_one({"_id": target_id})

        if not experiment:
            return {"message": f"Experiment with ID '{target_id}' not found."}, 404

        # 2. Serialize ObjectId fields to strings for JSON compatibility
        experiment["_id"] = str(experiment["_id"])
        if "participant_id" in experiment and isinstance(experiment["participant_id"], ObjectId):
            experiment["participant_id"] = str(experiment["participant_id"])

        return experiment, 200