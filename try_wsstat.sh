#!/usr/bin/bash
$ wsstat -n 10 ws://hawking.array.io:8090
$ wsstat -n 10 -H '{"method": "call", "params": [1, "login", ["", ""]], "id": 2}' ws://hawking.array.io:8090
Traceback (most recent call last):
  File "/home/denis/.virtualenvs/array/bin/wsstat", line 11, in <module>
    sys.exit(wsstat_console())
  File "/home/denis/.virtualenvs/array/lib/python3.6/site-packages/wsstat/main.py", line 68, in wsstat_console
    client = WebsocketTestingClient(**vars(args))
  File "/home/denis/.virtualenvs/array/lib/python3.6/site-packages/wsstat/clients.py", line 84, in __init__
    self.extra_headers = dict([map(lambda x: x.strip(), kwargs['header'].split(':'))])
ValueError: dictionary update sequence element #0 has length 4; 2 is required
(array) denis@denis-Z370-HD3P:~/p/bitshares-stress-test$ wsstat -n 10 -H {"method": "call", "params": [1, "login", ["", ""]], "id": 2} ws://hawking.array.io:8090
usage: wsstat [-h] [-n TOTAL_CONNECTIONS] [-c MAX_CONNECTING_SOCKETS]
              [-H HEADER] [--demo] [-i]
              [websocket_url]
wsstat: error: unrecognized arguments: params: [1, login, [, ]], id: 2} ws://hawking.array.io:8090
$ wsstat -n 10 -H """{"method": "call", "params": [1, "login", ["", ""]], "id": 2}""" ws://hawking.array.io:8090
Traceback (most recent call last):
  File "/home/denis/.virtualenvs/array/bin/wsstat", line 11, in <module>
    sys.exit(wsstat_console())
  File "/home/denis/.virtualenvs/array/lib/python3.6/site-packages/wsstat/main.py", line 68, in wsstat_console
    client = WebsocketTestingClient(**vars(args))
  File "/home/denis/.virtualenvs/array/lib/python3.6/site-packages/wsstat/clients.py", line 84, in __init__
    self.extra_headers = dict([map(lambda x: x.strip(), kwargs['header'].split(':'))])
ValueError: dictionary update sequence element #0 has length 4; 2 is required
