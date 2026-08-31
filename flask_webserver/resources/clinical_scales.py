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

        # 1. Resolve participant ID (trying both ObjectId and string)
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

        # 2. Update participant document with clinical scales measurements
        self.database.update(
            id=target_p_id,
            data={
                "clinical_scales": clinical_scales_data
            }
        )

        return {"message": "Clinical scales successfully recorded."}, 200