from flask import request
from flask_restful import Resource
from marshmallow import Schema
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask_webserver.schemas.weights_schema import WeightsSchema


class SaveWeights(Resource):
    """Resource for handling participant workload weight submissions."""

    def __init__(self, participants_db):
        self.participants_db = participants_db

    def _schema(self) -> Schema:
        return WeightsSchema()

    def post(self, participant_id: str):
        """
        Submit pairwise comparison weights for a participant
        ---
        description: Record the pairwise workload comparison weights (summing to 15) for calculating Weighted NASA-TLX.
        tags:
          - participant
        parameters:
          - in: path
            name: participant_id
            description: ID of the active participant submitting category weights
            required: true
            schema:
              type: string
        requestBody:
          description: Key-value dictionary of workload dimension weights
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  weights:
                    type: object
                    example:
                      mental_demand: 5
                      physical_demand: 1
                      temporal_demand: 3
                      performance: 2
                      effort: 3
                      frustration: 1
        responses:
          200:
            description: Weights successfully updated
          400:
            description: Invalid request payload or missing participant ID
          404:
            description: Participant not found
        """
        # Load and validate payload using Marshmallow schema
        schema = self._schema()
        json_data = request.get_json() or {}
        errors = schema.validate(json_data)
        if errors:
            return {"message": "Invalid request payload", "errors": errors}, 400

        weights = json_data.get("weights", {})

        # Resolve string or BSON ObjectId
        try:
            target_id = ObjectId(participant_id)
        except InvalidId:
            target_id = participant_id

        # Update weights in participant document
        part_collection = getattr(
            self.participants_db,
            'collection',
            getattr(self.participants_db, 'table', None)
        )

        participant = part_collection.find_one({"_id": target_id}) if part_collection else None
        if not participant and isinstance(target_id, ObjectId):
            participant = part_collection.find_one({"_id": str(participant_id)})

        if not participant:
            return {"message": f"Participant with ID {participant_id} not found."}, 404

        self.participants_db.update(
            id=participant["_id"],
            data={"weights": weights}
        )

        return {"message": "Weights updated successfully."}, 200