from flask_restful import Resource
from bson.objectid import ObjectId
from bson.errors import InvalidId

from flask_webserver.common.mongo_db import MongoDB


class NextExperiment(Resource):

    def __init__(self, experiments_db: MongoDB, participants_db: MongoDB):
        self.experiments_db = experiments_db
        self.participants_db = participants_db

    def get(self, participant_db_id: str):
        ''' ---
            description: Poll to check if a new robotic experiment is ready or if session is finished
            tags:
              - experiment
            parameters:
              - in: path
                name: participant_db_id
                description: ID of the participant polling for tasks
                required: true
                schema:
                    type: string
            responses:
                200:
                    description: Returns status ('ready', 'waiting', or 'finished')
                    content:
                        application/json:
                            schema:
                                type: object
                                properties:
                                    status:
                                        type: string
                                    experiment_id:
                                        type: string
                                    experiment_number:
                                        type: integer
                                    extra_step:
                                        type: boolean
        '''
        # Access collection via .collection or .table depending on your wrapper
        exp_collection = getattr(self.experiments_db, 'collection', getattr(self.experiments_db, 'table', None))
        
        if exp_collection is not None and hasattr(exp_collection, 'find_one'):
            ready_exp = exp_collection.find_one({
                "participant_id": str(participant_db_id),
                "status": "ready"
            })
        else:
            ready_exp = None

        if ready_exp:
            exp_id = str(ready_exp.get("_id") or ready_exp.get("id"))
            exp_num = ready_exp.get("experiment_number", 1)
            exp_extra_step = ready_exp.get("extra_step", False)
            return {
                "status": "ready",
                "experiment_id": exp_id,
                "experiment_number": exp_num,
                "extra_step": exp_extra_step
            }, 200

        # Check participant status using dump_from_id
        next_exp_num = 1  # Default next experiment number
        try:
            participant = getattr(self.participants_db, 'collection', getattr(self.participants_db, 'table', None)).find_one({"_id": ObjectId(participant_db_id)})
            next_exp_num = participant.get("next_experiment_number", 1)
            if participant and participant.get("is_finished"):
                return {"status": "finished"}, 200
        except InvalidId:
            pass

        return {
            "status": "waiting",
            "next_experiment_number": next_exp_num
        }, 200