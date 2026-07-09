# PeTRA Job Manager

## How to start

With docker only do:
```bash
source start_docker.sh
```

Reset database and give example data with:
```bash
python3 src/petra_central_control/flask_webserver/common/create_example_data.py
```

Start flask webserver
```bash
flask run -h 172.31.1.235 -p 5000
```

Start ros2 node:
```bash
ros2 launch petra_central_control job_manager.launch.py
```


## How to change IP Adress

Single place to change the IP Adress are the environment variables.
Or change them in the `.env` file.

If hosted on NUC, use `172.31.1.235`

```bash
PETRA_DATABASE_URI=mongodb://localhost:27017
FLASK_BACKEND_URL=http://localhost:5000
PETRA_FRONTEND_URL=http://localhost:3000
```

## Troubleshooting

If the follwing error occurs:
```bash
File "/usr/local/lib/python3.8/dist-packages/pymongo/pool.py", line 1278, in _get_socket
    sock_info = self.sockets.popleft()
IndexError: pop from an empty deque

#or

raise err
  File "/usr/local/lib/python3.8/dist-packages/urllib3/util/connection.py", line 86, in create_connection
    sock.connect(sa)
ConnectionRefusedError: [Errno 111] Connection refused
```

Then the database is not yet ready to accept connections. 
The wait time between the start of the database and the start of the webserver is not long enough. 
Increase the wait time in the env variable: 

```bash
WAIT_AFTER=5
```

## Unit Test (HAS TO WORK!)

Terminal 1:  
Start docker with main application and keep it open for all tests
```bash
source start_docker.sh
```

### TEST getting a new unstarted transport
Terminal 2:
```bash
docker exec -it petra_central_control bash
source install/setup.bash
ros2 service call /GetTransport petra_interfaces/srv/GetTransport
```
Expected response in terminal 2:
```bash
waiting for service to become available...
requester: making request: petra_interfaces.srv.GetTransport_Request(id=0)

response:
petra_interfaces.srv.GetTransport_Response(data=<...>)
```
Expected response from terminal 1:
```bash
127.0.0.1 - - [30/Mar/2023 21:41:54] "GET /transport/1 HTTP/1.1" 200 -
[job_manager-1] [INFO] [1680205314.446425799] [job_manager]: Current transport 1 has state 0
```

### TEST updating the current transport status
Terminal 2:
```bash
ros2 service call /UpdateTransport petra_interfaces/srv/UpdateTransport "{data: {id: 1, status: 1}, updated_keys: ['status']}"
```
Expected response in terminal 2:
```bash
waiting for service to become available...
requester: making request: petra_interfaces.srv.UpdateTransport_Request(data=<...>)

response:
petra_interfaces.srv.UpdateTransport_Response(success=True)
```
Expected response from terminal 1:
```bash
[job_manager-1] [INFO] [1680205848.453537279] [job_manager]: Current transport 1 has state 1
127.0.0.1 - - [30/Mar/2023 21:50:48] "GET /transport/1 HTTP/1.1" 200 -
```

### TEST getting the emergency state
Terminal 3:  
Attach a new shell for recieving the emergency message.  
After performing the service call, a message should appear in this bash.
```bash
docker exec -it petra_central_control bash
source install/setup.bash
ros2 topic echo /patient_state
```
Terminal 2:  
Update status to 2 (Has to be updatetd for new enums. This should be the EMERGENCY case number)
```bash
ros2 service call /UpdateTransport petra_interfaces/srv/UpdateTransport "{data: {id: 1, status: 7}, updated_keys: ['status']}"
```
Expected response in terminal 2:
```bash
waiting for service to become available...
requester: making request: petra_interfaces.srv.UpdateTransport_Request(data=<...>)

response:
petra_interfaces.srv.UpdateTransport_Response(success=True)
```
Expected response from terminal 1:
```bash
127.0.0.1 - - [30/Mar/2023 22:01:11] "GET /transport/1 HTTP/1.1" 200 -
[job_manager-1] [INFO] [1680206471.946671549] [job_manager]: Current transport 1 has state 2
[job_manager-1] [INFO] [1680206471.947072461] [job_manager]: EMERGENCY FROM TABLET!
```

Expected response from terminal 3:
```bash
header:
  stamp:
    sec: 1680206497
    nanosec: 446947985
  frame_id: tablet
image_header:
  stamp:
    sec: 0
    nanosec: 0
  frame_id: ''
state: 1
---
```

### TEST get current map 
Terminal 2:
```bash
ros2 launch petra_central_control test_map.launch.py
```
Expected response in terminal 2:
```bash
# [..]
[test_map-2] [INFO] [1682001059.179052986] [test_map]: Map loaded
[test_map-2] builtin_interfaces.msg.Time(sec=1682001058, nanosec=647597339)
[test_map-2] 0.10000000149011612
[test_map-2] 250
[test_map-2] 560
[test_map-2] -12.5
[test_map-2] -35.0
[test_map-2] 0.0
[test_map-2] geometry_msgs.msg.Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
```
The test map is located here:
[ros/maps/aws_robomaker_hospital.pgm](ros/maps/aws_robomaker_hospital.pgm)  
(display in VSCode with PGM viewer extension)

### Test update pose and path
Terminal 2:
```bash
ros2 launch petra_central_control test_map.launch.py
```
Terminal 3:  
Attach a new shell for sending the pose message.  
```bash
docker exec -it petra_central_control bash
source install/setup.bash
ros2 topic pub --once /update_pose geometry_msgs/msg/PoseStamped "{pose: {position: {x: 2, y: 2}}}"
```
Expected response in terminal 2:
```bash
# [..]
[test_map-2] [INFO] [1682700555.903867957] [test_map]: Received new robot pose
[test_map-2] On map: 2.0 in pixels: 144
[test_map-2] On map: 2.0 in pixels: 369
[test_map-2] geometry_msgs.msg.Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
```
Terminal 3:  
Send example path
```bash
ros2 topic pub --once /update_path nav_msgs/msg/Path "{poses: [{pose: {position: {x: 2, y: 2}}}, {pose: {position: {x: 2.25, y: 2}}}, {pose: {position: {x: 2.5, y: 2}}}, {pose: {position: {x: 2.75, y: 2}}}, {pose: {position: {x: 3, y: 2}}}, {pose: {position: {x: 3, y: 2.5}}}]}"
```
Expected response in terminal 2:
```bash
[test_map-2] [INFO] [1682700333.784795858] [test_map]: Received new path
[test_map-2] On map: (2.0, 2.0) in pixels: (144, 369)
[test_map-2] On map: (2.25, 2.0) in pixels: (147, 369)
[test_map-2] On map: (2.5, 2.0) in pixels: (149, 369)
[test_map-2] On map: (2.75, 2.0) in pixels: (152, 369)
[test_map-2] On map: (3.0, 2.0) in pixels: (154, 369)
[test_map-2] On map: (3.0, 2.5) in pixels: (154, 374)
```

## Test Flask Webserver

(May be deprecated)  
```bash
curl http://localhost:5000/transports
curl http://localhost:5000/transports -d '{"data":"This is transport1 data", "name":"Peter"}' -X POST
curl http://localhost:5000/transports -X DELETE

curl http://localhost:5000/transport/1 -d '{"data":"This is new transport1 data", "name":"Hans"}' -X PUT
curl http://localhost:5000/transport/1
curl http://localhost:5000/transport/1 -X DELETE

curl http://localhost:5000/users
curl http://localhost:5000/users -d '{"username":"Peter", "password":"123"}' -X POST
curl http://localhost:5000/users -X DELETE

curl http://localhost:5000/user/Peter -d '{"password":"12345"}' -X PUT
curl http://localhost:5000/user/Peter
curl http://localhost:5000/user/Peter -X DELETE

curl http://localhost:5000/login -d '{"username":"Peter", "password":"123"}' -X POST
curl http://localhost:5000/logout

-H "Content-Type: application/json"
```

## Start MongoDB

```bash
source start_db.sh
```

Without Docker from local system
```bash
sudo systemctl start mongod
sudo systemctl status mongod
sudo systemctl stop mongod
```
    