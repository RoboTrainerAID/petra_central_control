from marshmallow import Schema
from bson.objectid import ObjectId
from bson.errors import InvalidId

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.resources.validated_resource import ValidatedResource
from flask_webserver.schemas.clinical_scales_schema import ClinicalScalesSchema


class ClinicalScales(ValidatedResource):

    def __init__(self, participants_db: MongoDB):
        super().__init__(database=participants_db)

    def _schema(self) -> Schema:
        return ClinicalScalesSchema()

    def get(self, participant_id: str):
        ''' ---
            description: Get clinical scales of a participant by userId
            tags:
              - participant
            parameters:
              - in: path
                name: participant_id
                description: ID of the participant
                required: true
                schema:
                    type: string
            responses:
                200:
                    description: Clinical scales retrieved successfully
                404:
                    description: Participant not found
        '''
        participants_collection = getattr(
            self.database, 'collection', getattr(self.database, 'table', None)
        )

        participant = None
        try:
            participant = participants_collection.find_one({"_id": ObjectId(participant_id)})
        except InvalidId:
            pass

        if not participant:
            participant = participants_collection.find_one({"_id": participant_id})

        if not participant:
            return {"message": f"Participant with ID '{participant_id}' not found."}, 404

        clinical_scales = participant.get("clinical_scales", {})
        return {"user_id": participant_id, "clinical_scales": clinical_scales}, 200

    def post(self, participant_id: str):
        ''' ---
            description: Save clinical scales assessment data for a participant
            tags:
              - participant
            parameters:
              - in: path
                name: participant_id
                description: ID of the participant receiving clinical scales assessment
                required: true
                schema:
                    type: string
            requestBody:
                description: Clinical scales evaluation measurements payload
                required: true
                content:
                    application/json:
                        schema: ClinicalScalesSchema
            responses:
                200:
                    description: Clinical scales recorded successfully
                400:
                    description: Invalid request payload or participant ID
                404:
                    description: Participant not found
        '''
        clinical_scales_data = self.load_from_request()

        participants_collection = getattr(
            self.database, 'collection', getattr(self.database, 'table', None)
        )

        participant = None
        target_p_id = participant_id

        try:
            target_p_id = ObjectId(participant_id)
            participant = participants_collection.find_one({"_id": target_p_id})
        except InvalidId:
            pass

        if not participant:
            target_p_id = participant_id
            participant = participants_collection.find_one({"_id": target_p_id})

        if not participant:
            return {"message": f"Participant with ID '{participant_id}' not found."}, 404

        self.database.update(
            id=target_p_id,
            data={
                "clinical_scales": clinical_scales_data
            }
        )

        return {"message": "Clinical scales successfully recorded."}, 200
