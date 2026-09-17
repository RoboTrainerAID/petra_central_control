from flask_restful import Resource
from bson.objectid import ObjectId
from bson.errors import InvalidId

from flask_webserver.common.mongo_db import MongoDB




class WaitingExperiment(Resource):

    def __init__(self, experiments_db: MongoDB, participants_db: MongoDB):
        self.experiments_db = experiments_db
        self.participants_db = participants_db

    def get(self, participant_id: str):
        ''' ---
            description: Pull to get the id of current waiting experiment for a participant
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
                    description: Returns experiment_id of the waiting experiment or None if no waiting experiment exists
                    content:
                        application/json:
                            schema:
                                type: object
                                properties:
                                    experiment_id:
                                        type: string
        '''
        # Access collection via .collection or .table depending on your wrapper
        exp_collection = getattr(self.experiments_db, 'collection', getattr(self.experiments_db, 'table', None))
        
        if exp_collection is not None and hasattr(exp_collection, 'find_one'):
            waiting_exp = exp_collection.find_one({
                "participant_id": str(participant_id),
                "status": "waiting"
            })
        else:
            waiting_exp = None

        if waiting_exp:
            exp_id = str(waiting_exp.get("_id") or waiting_exp.get("id"))
            return exp_id, 200

        # Check participant status using dump_from_id
        try:
            participant = getattr(self.participants_db, 'collection', getattr(self.participants_db, 'table', None)).find_one({"_id": ObjectId(participant_id)})
            if participant and participant.get("is_finished"):
                return {"status": "finished"}, 200
        except InvalidId:
            pass

        return {"status": "not_found"}, 404