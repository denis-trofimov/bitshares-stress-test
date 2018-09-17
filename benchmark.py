# encoding: utf-8
# Konstantin Cyber, [13.09.18 17:29]
# так как для сценария будут ридонли операции необходимо продумать что-то осмысленное, например, типовой сценарий для блокчейн-эксплоера
# 1) запрос блока
# 2) запрос транзакции в блоке
# 3) запрос параметров БС
# 4) запрос глобальных параметров БЧ
#
# Konstantin Cyber, [13.09.18 17:30]
# вот тут перваая секция
# http://docs.bitshares.org/api/database.html
#
# Konstantin Cyber, [13.09.18 17:30]
# get_block, get_transaction, get_chain_properties, get_global_properties, get_config, get_chain_id, get_dynamic_global_properties, get_accounts

import os
import sys
import bitshares
import unittest
import json
from bitshares import BitShares

import logging
log = logging.getLogger()

network = bitshares.BitShares("ws://newton.array.io:8090", nobroadcast=True, debug=True)
# Obtain the content of one block
from bitshares.block import Block
print(Block(1))
Block()
