from flask import request
from flask_restful import Resource
from marshmallow import Schema
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask_webserver.schemas.ifis_schema import IFISSchema


class SaveIFIS(Resource):
    """Resource for saving International Fitness Scale questionnaire data."""

    def __init__(self, participants_db):
        self.participants_db = participants_db

    def _schema(self) -> Schema:
        return IFISSchema()

    def post(self, participant_id: str):
        """
        Submit International Fitness Scale (IFIS) responses for a participant
        ---
        description: Record the 5 IFIS questionnaire scores for a participant.
        tags:
          - participant
        parameters:
          - in: path
            name: participant_id
            description: ID of the participant submitting IFIS responses
            required: true
            schema:
              type: string
        requestBody:
          description: Dictionary of IFIS dimension scores (1=Very Poor to 5=Very Good)
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  ifis:
                    type: object
                    example:
                      general_fitness: 3
                      cardio_fitness: 4
                      muscle_strength: 3
                      speed_agility: 2
                      flexibility: 3
        responses:
          200:
            description: IFIS responses recorded successfully
          400:
            description: Invalid request payload
          404:
            description: Participant not found
        """
        json_data = request.get_json() or {}
        errors = self._schema().validate(json_data)
        if errors:
            return {"message": "Invalid request payload", "errors": errors}, 400

        part_collection = getattr(
            self.participants_db,
            'collection',
            getattr(self.participants_db, 'table', None)
        )

        participant = None
        try:
            participant = part_collection.find_one({"_id": ObjectId(participant_id)})
        except InvalidId:
            pass

        if not participant and part_collection:
            participant = part_collection.find_one({"_id": str(participant_id)})

        if not participant:
            return {"message": f"Participant with ID {participant_id} not found."}, 404

        # Save IFIS answers and finalize participant profile
        self.participants_db.update(
            id=participant["_id"],
            data={
                "ifis": json_data.get("ifis", {}),
                "is_finished": True,
                "status": "completed"
            }
        )

        return {"message": "IFIS responses saved successfully."}, 200