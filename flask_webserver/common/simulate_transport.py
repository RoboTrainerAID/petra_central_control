"""
Simulates a transport using the wheelchair mode
"""
import os
import sys
import time

from flask_webserver.common.simulation_util import get_all_transports, set_transport_state, wait_for_transport_state, \
    set_transport
from flask_webserver.schemas.enums import TransportStatus

if __name__ == "__main__":
    flask_webserver_ip = os.environ["FLASK_BACKEND_URL"]
    test_transport_id = 1
    with_platform = True  # set to True to simulate wheelchair transport
    with_platform_preset = False  # set to true to simulate previously assigned platform
    with_patient_emergency = True  # set to true to include waiting for a patient triggered emergency
    with_robot_emergency = True  # set to true to simulate a robot triggered emergency

    transports = get_all_transports()
    print(transports)

    # find test transport
    test_transport = None
    for transport in transports:
        if transport["_id"] == test_transport_id:
            test_transport = transport

    if test_transport is None:
        raise ValueError(f"Did not find transport with id: {test_transport_id}")

    # set all transports to done
    for transport in transports:
        set_transport_state(transport, TransportStatus.DONE)

    # set test transport to waiting and remove any assigned platform
    test_transport["platform_nr"] = 2 if with_platform_preset else -1
    set_transport(test_transport)

    test_transport = set_transport_state(test_transport, TransportStatus.WAITING)

    # petra is inbound after some time
    time.sleep(5)
    print("Petra inbound")
    test_transport = set_transport_state(test_transport, TransportStatus.INBOUND)

    # petra is waiting for platform if platform once arrived
    time.sleep(5)
    if with_platform:
        if test_transport["platform_nr"] < 0:
            print("Waiting for platform to be assigned")
            test_transport = set_transport_state(test_transport, TransportStatus.WAITING_FOR_PLATFORM)
            print("Platform has been assigned")
        else:  # if platform is already set, go into coupling immediately
            test_transport = set_transport_state(test_transport, TransportStatus.COUPLING)

        # waiting for coupling state
        test_transport = wait_for_transport_state(test_transport, TransportStatus.COUPLING)
        print("Coupling platform")

        # coupling takes a few seconds
        time.sleep(10)
        test_transport = set_transport_state(test_transport, TransportStatus.WAITING_FOR_SECURITY_CHECK)
        print("Waiting for security check and patient approval")
    else:
        test_transport = set_transport_state(test_transport, TransportStatus.WAITING_FOR_PATIENT_APPROVAL)
        print("Waiting for patient approval")

    # waiting for transport state to be running
    test_transport = wait_for_transport_state(test_transport, TransportStatus.RUNNING)
    print("Transport is starting")

    # wait for patient emergency
    if with_patient_emergency:
        print("Waiting for Emergency")
        test_transport = wait_for_transport_state(test_transport, TransportStatus.EMERGENCY_STOP)
        print("Emergency detected, please continue transport")
        test_transport = wait_for_transport_state(test_transport, TransportStatus.RUNNING, TransportStatus.DONE)
        if test_transport["status"] == TransportStatus.DONE.value:
            print("Transport Aborted")
            sys.exit(0)

        print("Continuing transport")

    # throw an emergency to check whether the emergency works
    if with_robot_emergency:
        time.sleep(5)
        test_transport = set_transport_state(test_transport, TransportStatus.EMERGENCY_PENDING)
        print("Emergency test")

        # wait for transport state to be either done or continue the transport
        test_transport = wait_for_transport_state(test_transport, TransportStatus.RUNNING, TransportStatus.DONE)

        if test_transport["status"] == TransportStatus.DONE.value:
            print("Transport aborted")
            sys.exit(0)

        print("continuing transport")

    time.sleep(5)
    if test_transport["platform_nr"] >= 0:
        test_transport = set_transport_state(test_transport, TransportStatus.WAITING_FOR_UNLOAD)
    else:
        test_transport = set_transport_state(test_transport, TransportStatus.DONE)
    print("Transport done")
