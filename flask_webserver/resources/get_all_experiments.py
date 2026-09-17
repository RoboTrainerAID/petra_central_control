from flask_restful import Resource
from bson.objectid import ObjectId
from bson.errors import InvalidId

from flask_webserver.common.mongo_db import MongoDB


class AllExperimentsFromUser(Resource):

    def __init__(self, experiments_db: MongoDB):
        self.experiments_db = experiments_db

    def get(self, participant_id: str):
        ''' ---
            description: Get all compleated experiments for a participant
            tags:
              - experiment
            parameters:
              - in: path
                name: participant_id
                description: ID of the participant 
                required: true
                schema:
                    type: string
            responses:
                200:
                    description: Returns all experiments for a participant
                    content:
                        application/json:
                            schema:
                                type: object
                                properties:
                                    experiments:
                                        type: array
                                        items:
                                            type: object
                404:
                    description: no experiments found for the participant
        '''
        # Access collection via .collection or .table depending on your wrapper
        exp_collection = getattr(self.experiments_db, 'collection', getattr(self.experiments_db, 'table', None))

        experiments_list = []
        if exp_collection is not None:
            # Query the database
            cursor = exp_collection.find({
                "participant_id": str(participant_id),  # Change to "userId" if your experiments collection uses userId instead
                "status": "completed"
            })
            
            # Convert cursor to list and fix ObjectId serialization
            for exp in cursor:
                exp["_id"] = str(exp["_id"])
                # If participant_id or other fields are also ObjectIds, convert them too:
                if "participant_id" in exp and not isinstance(exp["participant_id"], str):
                    exp["participant_id"] = str(exp["participant_id"])
                experiments_list.append(exp)

        return {"experiments": experiments_list}, 200

        return {"message": "No experiments found for the participant"}, 404
