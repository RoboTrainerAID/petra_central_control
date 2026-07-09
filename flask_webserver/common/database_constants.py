from enum import Enum


class TransportStatus(Enum):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    FINISHED = 2


class TransportMode(Enum):
    WHEELCHAIR = 0
    ROLLATOR = 1
    GUIDED_WALKING = 2
    TROLLEY = 3
    EMPTY = 4


class LocationType(Enum):
    ROOM = 0
    ELEVATOR = 1
    CHARGING = 2
    MATERIAL = 3
