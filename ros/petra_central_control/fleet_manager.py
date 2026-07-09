import requests
from flask_webserver.schemas.enums import TransportStatus


class FleetManager():

    def __init__(self, flask_webserver_url):

        self.flask_webserver_url = flask_webserver_url

    def get_optimal_next_transport(self):
        """ simple implementaion only gives oldest transport (smallest _id) of all unstarted jobs
        """

        r = requests.get(self.flask_webserver_url + "transports")

        if r.status_code != 200:
            return None
        
        unstarted_transports = [transport for transport in r.json() if transport["status"] == TransportStatus.WAITING.value]

        if len(unstarted_transports) == 0:
            return None

        unstarted_transports.sort(key=lambda x: x.get("_id"))
        return unstarted_transports[0]
