import urllib.parse

from apispec.ext.marshmallow import MarshmallowPlugin
from marshmallow import fields, Schema

from flask_webserver.common.mongo_db import MongoDB
from flask_webserver.resources.location_list import LocationList
from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api
from apispec import APISpec
from apispec_flask_restful import RestfulPlugin
# from apispec_webframeworks.flask import FlaskPlugin
# from flask_pymongo import PyMongo
import json

from flask_webserver.resources.payload import Payload
from flask_webserver.resources.payload_list import PayloadList
from flask_webserver.resources.robot_map_relay import RobotMapRelay
from flask_webserver.resources.robot_path_relay import RobotPathRelay
from flask_webserver.resources.robot_position_relay import RobotPositionRelay
from flask_webserver.resources.transport import Transport
from flask_webserver.resources.transport_list import TransportList
from flask_webserver.resources.user import User
from flask_webserver.resources.user_list import UserList
from flask_webserver.resources.location import Location
from flask_webserver.resources.location_list import LocationList
from flask_webserver.common.authentication import Authentication
import os

from flask_webserver.schemas.error_schema import ValidationErrorSchema, SingleMessageErrorSchema
from flask_webserver.schemas.payload_schema import PayloadSchema

app = Flask(__name__)
frontend_url = os.environ["PETRA_FRONTEND_URL"]

cors = CORS(app=app, origins=[
            frontend_url,
            "http://localhost:3000"])
api = Api(app)
spec = APISpec(
    title="PeTRA Job Manager",
    version="1.0.0",
    openapi_version="3.0.2",
    info=dict(
        description="Job Manager for PeTRA transports",
        version="1.0.0",
        contact=dict(
            email="Andreas.Zachariae@gmail.com"
        )
    ),
    servers=[dict(
        description="Flask",
        url="http://192.168.0.50:5000/"
    )
    ],
    tags=[dict(
        name="transport",
        description="Access to transport data"),
        dict(
        name="user",
        description="Access to user data")],
    plugins=[RestfulPlugin(), MarshmallowPlugin()],  # FlaskPlugin()
)


@app.route("/")
def hello_world():
    return {"response": "Hello World!"}


@app.route("/login", methods=['POST'])
def login():
    json_data = request.get_json(force=True)
    return Authentication.login(username=json_data['username'],
                                password=json_data['password'])


@app.route("/logout")
def logout():
    return Authentication.logout()


local_dicts = {}


def storeDict(name: str, data: dict):
    local_dicts[name] = data


def getDict(name: str):
    if name in local_dicts.keys():
        return local_dicts[name]
    return None


transports_db = MongoDB(table="transports")
locations_db = MongoDB(table="locations")
payloads_db = MongoDB(table="payloads")
users_db = MongoDB(table="users")

transports_args = {
    'transports_db': transports_db,
    'locations_db': locations_db,
    'payloads_db': payloads_db,
}

locations_args = {
    'locations_db': locations_db,
}

payloads_args = {
    'payloads_db': payloads_db,
    'locations_db': locations_db,
}

users_args = {
    'users_db': users_db,
}

local_dicts_args = {
    'storeDict': storeDict,
    'getDict': getDict,
}

api.add_resource(TransportList, '/transports', resource_class_kwargs=transports_args)
api.add_resource(Transport, '/transport/<int:transport_id>', resource_class_kwargs=transports_args)
api.add_resource(UserList, '/users', resource_class_kwargs=users_args)
api.add_resource(User, '/user/<username>', resource_class_kwargs=users_args)
api.add_resource(LocationList, '/locations', resource_class_kwargs=locations_args)
api.add_resource(Location, '/location/<int:location_id>', resource_class_kwargs=locations_args)
api.add_resource(PayloadList, '/payloads', resource_class_kwargs=payloads_args)
api.add_resource(Payload, '/payload/<int:payload_id>', resource_class_kwargs=payloads_args)
api.add_resource(RobotPositionRelay, '/relay/position', resource_class_kwargs=local_dicts_args)
api.add_resource(RobotPathRelay, '/relay/path', resource_class_kwargs=local_dicts_args)
api.add_resource(RobotMapRelay, '/relay/map', resource_class_kwargs=local_dicts_args)

spec.path(resource=Transport, api=api)
spec.path(resource=TransportList, api=api)
spec.path(resource=User, api=api)
spec.path(resource=UserList, api=api)
spec.path(resource=Location, api=api)
spec.path(resource=LocationList, api=api)
spec.path(resource=Payload, api=api)
spec.path(resource=PayloadList, api=api)
spec.path(resource=RobotPositionRelay, api=api)
spec.path(resource=RobotPathRelay, api=api)
spec.path(resource=RobotMapRelay, api=api)

# add error schemas to json
#spec.components.schema("ValidationErrorSchema", ValidationErrorSchema)
#spec.components.schemas("SingleMessageErrorSchema", SingleMessageErrorSchema)

# with app.test_request_context():
#     spec.path(view=hello_world)

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "openapi/specification.json"), 'w') as f:
    json.dump(spec.to_dict(), f, indent=4)

if __name__ == "__main__":
    # currently not used with "flask run" command
    hostname = urllib.parse.urlparse(os.environ["FLASK_BACKEND_URL"]).hostname
    port = urllib.parse.urlparse(os.environ["FLASK_BACKEND_URL"]).port
    app.run(host=hostname, port=port, debug=True)
