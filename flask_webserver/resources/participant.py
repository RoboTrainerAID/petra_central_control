from flask import request
from marshmallow import Schema
from bson.errors import InvalidId

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.resources.validated_resource import ValidatedResource
from flask_webserver.schemas.participant_schema import ParticipantSchema


class Participant(ValidatedResource):

    def __init__(self, participants_db: MongoDB):
        super().__init__(database=participants_db)

    def _schema(self) -> Schema:
        return ParticipantSchema()

    def post(self, userId: str):
        ''' ---
            description: Register a new participant in the database
            tags:
              - participant
            parameters:
              - in: path
                name: userId
                description: userId of the participant
                required: true
                schema:
                    type: string
            responses:
                201:
                    description: Participant registered successfully and first experiment created
                    content:
                        application/json:
                            schema:
                                type: object
                                properties:
                                    participant_db_id:
                                        type: string
                400:
                    description: Invalid request payload or participant ID
                409:
                    description: Participant already exists
        '''
        # Check whether the userId already exists 
        existing_participants = self.database.select_filtered({ "userId": userId }) 
        if existing_participants: 
            return { "message": f"Participant with userId '{userId}' already exists." }, 409 
        # Create the participant 
        participant = { "userId": userId, "is_finished": False } 
        # Insert participant into the database 
        result = self.database.insert(participant) 
        inserted_id = getattr(result, "inserted_id", result)
        participant_db_id = str(inserted_id)
        return {"participant_db_id": participant_db_id}, 201
    
    def get(self, userId: str):
        ''' ---
            description: Get participant details by userId
            tags:
              - participant
            parameters:
              - in: path
                name: userId
                description: userID of the participant
                required: true
                schema:
                    type: string
            responses:
                200:
                    description: Participant retrieved successfully
                404:
                    description: Participant not found
        '''
        participants_collection = getattr(
            self.database, 'collection', getattr(self.database, 'table', None)
        )

        participant = None
        try:
            participant = participants_collection.find_one({"userId": userId})
        except InvalidId:
            pass

        if not participant:
            participant = participants_collection.find_one({"userId": userId})

        if not participant:
            return {"message": f"Participant with ID '{userId}' not found."}, 404

        participant["_id"] = str(participant["_id"])
        return participant, 200

    def patch(self, userId: str = None, participant_id: str = None):
        """
        Update fields for an existing participant
        ---
        tags:
          - participant
        parameters:
          - in: path
            name: userId
            description: userId of the participant
            required: true
            schema:
              type: string
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  is_finished:
                    type: boolean
        responses:
          200:
            description: Participant updated successfully
          400:
            description: No update data provided
          404:
            description: Participant not found
        """
        target_id = userId or participant_id
        data = request.get_json() or {}
        if not data:
            return {"message": "No data provided to update."}, 400

        participants_collection = getattr(
            self.database, 'collection', getattr(self.database, 'table', None)
        )

        participant = participants_collection.find_one({"userId": target_id})
        if not participant:
            return {"message": f"Participant with userId '{target_id}' not found."}, 404

        self.database.update(
            id=participant["_id"],
            data=data
        )

        return {"message": f"Participant '{target_id}' updated successfully.", "updated_fields": data}, 200

        