import os
import time
import requests

flask_webserver_ip = os.environ["FLASK_BACKEND_URL"]
max_wait_time = 10

if __name__ == "__main__":
    start_time = time.time()
    while start_time + max_wait_time > time.time():
        try:
            response = requests.get(flask_webserver_ip + "/")
            if response.status_code == 200:
                break
        except:
            print("Waiting for flask webserver to start...")
            time.sleep(1)

    response = requests.delete(flask_webserver_ip + "/transports")
    response = requests.delete(flask_webserver_ip + "/locations")
    response = requests.delete(flask_webserver_ip + "/users")
    response = requests.delete(flask_webserver_ip + "/payloads")

    response = requests.post(
        flask_webserver_ip + "/locations", json={"name": "Materiallager", "type": 3, "position_x": -2.7, "position_y": 2.1, "quaternion_x": 0, "quaternion_y": 0, "quaternion_z": 0, "quaternion_w": 1, "floor": 1})
    print(response.text)

    response = requests.post(
        flask_webserver_ip + "/locations", json={"name": "Station A", "type": 0, "position_x": 2, "position_y": 2, "quaternion_x": 0, "quaternion_y": 0, "quaternion_z": 0, "quaternion_w": 1, "floor": 1})
    print(response.text)

    response = requests.post(
        flask_webserver_ip + "/locations", json={"name": "Station B", "type": 0, "position_x": 2, "position_y": 2, "quaternion_x": 0, "quaternion_y": 0, "quaternion_z": 0, "quaternion_w": 1, "floor": 1})
    print(response.text)

    response = requests.post(
        flask_webserver_ip + "/locations",
        json={"name": "Aufzug", "type": 1, "position_x": 2, "position_y": 2, "quaternion_x": 0, "quaternion_y": 0,
              "quaternion_z": 0, "quaternion_w": 1, "floor": 1})
    print(response.text)

    # response = requests.post(
    #     flask_webserver_ip + "/locations", json={"name": "Charger", "type": 2, "position_x": 2, "position_y": 2, "quaternion_x": 0, "quaternion_y": 0, "quaternion_z": 0, "quaternion_w": 1, "floor": 1})
    # print(response.text)
    # response = requests.post(flask_webserver_ip + "/transports", json={'status': 0,
    #                                                                    "mode": 0,
    #                                                                    "first_name": "Petra",
    #                                                                    "last_name": "Mueller",
    #                                                                    "language": "de",
    #                                                                    "start_time": "Wed Jul 21 2022 09:42:00 GMT+0200",
    #                                                                    "start_location": "Station A",
    #                                                                    "goal_time": "Wed Jul 21 2022 10:42:00 GMT+0200",
    #                                                                    "goal_location": "Station B",
    #                                                                    "platform_nr": 2})

    # print(response.text)

    response = requests.post(
        flask_webserver_ip + "/users", json={"username": "Petra", "password": "123"})
    
    response = requests.post(
        flask_webserver_ip + "/users", json={"username": "petra", "password": "123"})

    print(response.text)

    # create dummy patient
    # response = requests.post(f'{flask_webserver_ip}/payloads', json={
    #     'type': 0,
    #     'name': 'Andreas',
    #     'last_name': 'Zachariae',
    #     'location': 2,
    #     'preferred_language': 'de',
    #     'preferred_mode': 2,
    # })
    # print(response.text)

    response = requests.post(f'{flask_webserver_ip}/payloads', json={
        'type': 1,
        'name': 'Kiste',
        'location': 1,
        'preferred_mode': 3,
    })
    print(response.text)

    ## create dummy transport
    # response = requests.post(f'{flask_webserver_ip}/transports', json={
    #     'status': 0,
    #     'payload': 1,
    #     'override_mode': None,
    #     'override_start_location': None,
    #     'goal_location': 2,
    #     'is_start_time': True,
    #     'time_stamp': 1678284623725,
    #     'platform_nr': -1
    # })
    # print(response.text)
