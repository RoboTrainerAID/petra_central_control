from enum import IntEnum


class LocationType(IntEnum):
    """
    Types of locations
    """
    ROOM = 0
    ELEVATOR = 1
    CHARGING = 2
    STORAGE = 3


def is_location_type_valid(value: int) -> bool:
    """
    Checks if the given integer could be a location type
    :param value: the integer to check
    :return: whether the given value could be a payload type
    """
    return value in [l_type.value for l_type in LocationType]


class PayloadType(IntEnum):
    """
    Types of payloads
    """
    PATIENT = 0
    CARGO = 1


def is_payload_type_valid(value: int) -> bool:
    """
    Checks if the given integer could be a payload type
    :param value: the integer to check
    :return: whether the given value could be a payload type
    """
    return value in [p_type.value for p_type in PayloadType]


class TransportMode(IntEnum):
    """
    Transport modes for human transport
    """
    WHEEL_CHAIR = 0
    FREE_WALKING = 1
    GUIDED_WALKING = 2
    ON_BOARD = 3
    TRAILER = 4


def is_transport_mode_valid(value: int) -> bool:
    """
    Checks if the given value could be a transport mode
    :param value: the value to be checked
    :return: whether the given value could be a transport mode
    """
    return value in [t_mode.value for t_mode in TransportMode]


class TransportStatus(IntEnum):
    """
    States a transport can be in
    """
    WAITING = 0
    INBOUND = 1
    WAITING_FOR_PLATFORM = 2
    COUPLING = 3
    WAITING_FOR_SECURITY_CHECK = 4
    WAITING_FOR_PATIENT_APPROVAL = 5
    RUNNING = 6
    EMERGENCY_PENDING = 7
    EMERGENCY_STOP = 8
    WAITING_FOR_UNLOAD = 9
    DONE = 10


def is_transport_status_valid(value: int) -> bool:
    """
    Checks if the given value could be a transport status
    :param value: the value to be checked
    :return: whether the given value could be a transport type
    """
    return value in [t_status.value for t_status in TransportStatus]
