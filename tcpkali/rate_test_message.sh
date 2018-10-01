tcpkali -T 200 -vvv -c10 -r400 --ws \
-1 '{"method": "call", "params": [1, "database", []], "id": 3}' \
 -m '{"method": "call", "params": [2, "get_block", [\{re [0-9]{1,4}}]], "id": 7}' \
 hawking.array.io:8090 2>&1 | tee rate400_c10.log

 tcpkali -T 60 -vvv -c6 -r1000 --ws \
-1 '{"method": "call", "params": [1, "database", []], "id": 3}' \
 -m '{"method": "call", "params": [2, "get_block", [\{re [0-9]{1,4}}]], "id": 7}' \
 hawking.array.io:8090 2>&1 | tee rate1000_c6.log

 tcpkali -T 180 -vvv -c12 -r400 --ws -1 '{"method": "call", "params": [1, "database", []], "id": 3}'  -m '{"method": "call", "params": [2, "get_block", [\{re [0-9]{1,3}}]], "id": 7}'  hawking.array.io:8090 2>&1 | tee rate400_c12_sec180.log
