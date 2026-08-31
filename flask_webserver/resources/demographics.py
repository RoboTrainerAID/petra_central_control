from flask import request
from flask_restful import Resource
from marshmallow import Schema
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask_webserver.schemas.demographics_schema import DemographicsSchema


class SaveDemographics(Resource):
    """Resource for handling participant demographic data submissions."""

    def __init__(self, participants_db):
        self.participants_db = participants_db

    def _schema(self) -> Schema:
        return DemographicsSchema()

    def post(self, participant_id: str):
        """
        Submit demographic information for a participant
        ---
        description: Record demographic details for a participant upon survey completion.
        tags:
          - participant
        parameters:
          - in: path
            name: participant_id
            description: ID of the participant submitting demographic responses
            required: true
            schema:
              type: string
        requestBody:
          description: Key-value dictionary of demographic attributes
          required: true
          content:
            application/json:
              schema: DemographicsSchema
        responses:
          200:
            description: Demographics recorded successfully
          400:
            description: Invalid request payload
          404:
            description: Participant not found
        """
        json_data = request.get_json() or {}
        
        # Validate input against schema
        errors = self._schema().validate(json_data)
        if errors:
            return {"message": "Invalid request payload", "errors": errors}, 400

        participants_collection = getattr(
            self.participants_db,
            'collection',
            getattr(self.participants_db, 'table', None)
        )

        # Resolve participant ID (tries BSON ObjectId, falls back to string)
        participant = None
        try:
            participant = participants_collection.find_one({"_id": ObjectId(participant_id)})
        except InvalidId:
            pass

        if not participant and participants_collection:
            participant = participants_collection.find_one({"_id": str(participant_id)})

        if not participant:
            return {"message": f"Participant with ID {participant_id} not found."}, 404

        # Save demographics and mark participant as completely finished
        self.participants_db.update(
            id=participant["_id"],
            data={
                "demographics": json_data,
                "is_finished": True,
                "status": "completed"
            }
        )

        return {"message": "Demographics saved successfully."}, 200