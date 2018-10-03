#!/usr/bin/env bash #lends you some flexibility on different systems
tcpkali -vv --ws -c12 -r @500ms --connect-timeout 3 \
--latency-marker "transaction_merkle_root" --message-stop "Assert Exception" \
-1 '{"method": "call", "params": [1, "database", []], "id": 3}' \
-m '{"method": "call", "params": [2, "get_block", [\{connection.uid}]], "id": 7}' \
newton.array.io:8090  2>&1 | tee latency_500ms.log

tcpkali -vv --ws -c100 -r @1000ms --connect-rate 10 \
--latency-marker "transaction_merkle_root" --message-stop "Assert Exception" \
-1 '{"method": "call", "params": [1, "database", []], "id": 3}' \
-m '{"method": "call", "params": [2, "get_block", [\{connection.uid}]], "id": 7}' \
newton.array.io:8090  2>&1 | tee latency_r@1000ms_c100.log

tcpkali -vv --ws -c10 -r @1000ms \
--latency-marker "transaction_merkle_root" --message-stop "Assert Exception" \
-1 '{"method": "call", "params": [1, "database", []], "id": 3}' \
-m '{"method": "call", "params": [2, "get_block", [\{connection.uid}]], "id": 7}' \
newton.array.io:8090  2>&1 | tee latency_r@1000ms_c10_gpon.log

tcpkali -vv --ws -c2 -r @1000ms \
--latency-marker "transaction_merkle_root" --message-stop "Assert Exception" \
-1 '{"method": "call", "params": [1, "database", []], "id": 3}' \
-m '{"method": "call", "params": [2, "get_block", [\{connection.uid}]], "id": 7}' \
newton.array.io:8090  2>&1 | tee latency_r@1000ms_c2_gpon.log

tcpkali -vv --ws -c6 -r @1000ms \
--latency-marker "transaction_merkle_root" --message-stop "Assert Exception" \
-1 '{"method": "call", "params": [1, "database", []], "id": 3}' \
-m '{"method": "call", "params": [2, "get_block", [\{connection.uid}]], "id": 7}' \
newton.array.io:8090  2>&1 | tee latency_r@1000ms_c6_gpon.log

tcpkali -vv --ws -c24 -r @1000ms \
--latency-marker "transaction_merkle_root" --message-stop "Assert Exception" \
-1 '{"method": "call", "params": [1, "database", []], "id": 3}' \
-m '{"method": "call", "params": [2, "get_block", [\{connection.uid}]], "id": 7}' \
newton.array.io:8090  2>&1 | tee latency_r@1000ms_c24_gpon.log

tcpkali -vv --ws -c12 -r @1000ms \
--latency-marker "transaction_merkle_root" --message-stop "Assert Exception" \
-1 '{"method": "call", "params": [1, "database", []], "id": 3}' \
-m '{"method": "call", "params": [2, "get_block", [\{connection.uid}]], "id": 7}' \
newton.array.io:8090  2>&1 | tee latency_r@1000ms_c12_gpon.log

tcpkali -vv --ws -c24 -r @2000ms \
--latency-marker "transaction_merkle_root" --message-stop "Assert Exception" \
-1 '{"method": "call", "params": [1, "database", []], "id": 3}' \
-m '{"method": "call", "params": [2, "get_block", [\{connection.uid}]], "id": 7}' \
newton.array.io:8090  2>&1 | tee latency_r@2000ms_c24_gpon.log
