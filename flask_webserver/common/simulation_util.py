"""
Utility functions for simulation scripts
"""
import os
import time
from typing import List

import requests

from flask_webserver.schemas.enums import TransportStatus

flask_webserver_ip = os.environ["FLASK_BACKEND_URL"]


def get_all_transports() -> List[dict]:
    """
    Retrieves a list of all registered transports
    :return:
    """
    return requests.get(f"{flask_webserver_ip}/transports").json()


def set_transport(transport: dict):
    """
    Sets the given transport to the given values
    :param transport:
    :return:
    """
    tmp_json = {**transport}
    del tmp_json['_id']
    del tmp_json['duration']

    requests.put(f"{flask_webserver_ip}/transport/{transport['_id']}", json=tmp_json)


def get_transport(transport: dict) -> dict:
    """
    Retrieves the current values of the given transport from the server
    :param transport:
    :return: the values given by the server
    """
    return requests.get(f"{flask_webserver_ip}/transport/{transport['_id']}").json()


def set_transport_state(transport: dict, state: TransportStatus) -> dict:
    """
    Sets the state of the given transport
    :param transport:
    :param state:
    :return: the new transport details
    """
    transport["status"] = state.value
    set_transport(transport)

    return get_transport(transport)


def wait_for_transport_state(transport: dict, *states: TransportStatus) -> dict:
    """
    Waits until the given transports state is one of the given states
    :param transport:
    :param states:
    :return: the transport details when the state is reached
    """
    transport = get_transport(transport)
    while not any(state.value == transport["status"] for state in states):
        time.sleep(1)
        transport = get_transport(transport)

    return transport
