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

from bitshares import BitShares

import logging
log = logging.getLogger()

b1 = BitShares(
    "wss://node.testnet.bitshares.eu",
    nobroadcast=True,
)

b2 = BitShares(
    "wss://node.bitshares.eu",
    nobroadcast=True,
)

unittest.TestCase.assertNotEqual(b1.rpc.url, b2.rpc.url)
