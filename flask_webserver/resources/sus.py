import os
import json
from flask import request
from flask_restful import Resource
from marshmallow import Schema
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask_webserver.schemas.sus_schema import SusSchema


class SaveSus(Resource):
    """Resource for handling SUS questionnaire submissions."""
    
    def __init__(self, participants_db, experiments_db):
        self.participants_db = participants_db
        self.experiments_db = experiments_db
        self.data_dir = os.environ.get("DATA_DIR", "/home/docker/data")  # Default to /home/docker/data if not set

    def _schema(self) -> Schema:
        return SusSchema()

    def post(self, participant_id: str):
        """
        Submit SUS responses for a participant
        ---
        description: Record System Usability Scale (1-5 Likert scale) responses and calculate total SUS score (0-100).
        tags:
          - participant
        parameters:
          - in: path
            name: participant_id
            description: ID of the participant submitting SUS responses
            required: true
            schema:
              type: string
        requestBody:
          description: SUS 10-item response dictionary
          required: true
          content:
            application/json:
              schema: SusSchema
        responses:
          200:
            description: SUS responses recorded successfully
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

        exp_collection = getattr(
            self.experiments_db,
            'collection',
            getattr(self.experiments_db, 'table', None)
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

        # Calculate standard SUS Score (0 - 100)
        # Odd questions (q1, q3, q5, q7, q9): score - 1
        # Even questions (q2, q4, q6, q8, q10): 5 - score
        sus_items = [
            json_data["q1"] - 1,
            5 - json_data["q2"],
            json_data["q3"] - 1,
            5 - json_data["q4"],
            json_data["q5"] - 1,
            5 - json_data["q6"],
            json_data["q7"] - 1,
            5 - json_data["q8"],
            json_data["q9"] - 1,
            5 - json_data["q10"]
        ]
        total_sus_score = sum(sus_items) * 2.5

        # Save SUS responses and final score
        self.participants_db.update(
            id=participant["_id"],
            data={
                "sus": {
                    "responses": json_data,
                    "score": total_sus_score
                },
                "is_finished": True,
                "status": "completed"
            }
        )
        
        # Also fetch all completed experiments associated with this participant
        experiments = list(exp_collection.find({'participant_id': participant_id}))

        # Helper function to recursively clean BSON types (like ObjectId and datetime) for JSON export
        def clean_bson(doc):
            if isinstance(doc, dict):
                return {k: clean_bson(v) for k, v in doc.items()}
            elif isinstance(doc, list):
                return [clean_bson(i) for i in doc]
            elif isinstance(doc, ObjectId):
                return str(doc)
            return doc

        full_record = {
            "participant": clean_bson(participant),
            "experiments": clean_bson(experiments)
        }

        # 3. Save to a JSON file in the 'data/' directory
        file_path = os.path.join(self.data_dir, f"participant_{participant['userId']}.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(full_record, f, indent=4, ensure_ascii=False)
            print(f"Successfully saved record to {file_path}")
        except Exception as e:
            print(f"Error saving JSON file: {e}")

        return {"message": "SUS responses saved successfully.", "sus_score": total_sus_score}, 200