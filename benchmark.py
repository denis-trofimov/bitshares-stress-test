#!/usr/bin/python
# -*- coding: UTF-8 -*-
""" Scenario test, stress test tool for BitShares based on JSON and pybitshares.
    get_block, get_transaction, get_chain_properties, get_global_properties, get_config, get_chain_id, get_dynamic_global_properties, get_accounts
"""


import json
import logging
from bitshares import BitShares
from bitshares.block import Block, BlockHeader
from bitshares.blockchain import Blockchain


class Scenario(object):
    """ Scenario test, stress test tool for BitShares based on JSON and pybitshares.
    """
    def __init__(self, script_name: str ="scenario.json"):
        # try:
        with open(script_name, 'rt') as file:
            self.scenario = json.load(file)
        # except FileNotFoundError, Error
        if not self.scenario or not self.scenario.get("stages", 0):
            print("Empty stages!")

    def run(self):
        # Connect bitshares
        self.bts = BitShares("ws://newton.array.io:8090", nobroadcast=True, debug=True)

        for stage in self.scenario.get("stages", []):
            kwargs: dict = stage.get("params", {})
            result: str = getattr(self, stage.get("method", ''), lambda:None)(**kwargs)
            print(json.dumps(result))

    def get_global_properties(self):
        """ Retrieve the current global_property_object."""
        return self.bts.info()

    def get_block(self, block_num: int):
        """ Retrieve a full, signed block."""
        return Block(block_num, blockchain_instance=self.bts, lazy=False)

    def get_chain_properties(self):
        """ Retrieve the chain_property_object associated with the chain."""
        self.chain = Blockchain(mode="head")
        return self.chain.get_chain_properties()

    def get_dynamic_global_properties(self):
        """ This call returns the *dynamic global properties*
        """
        return self.chain.info()

    def get_config(self) -> str:
        """ Retrieve compile-time constants."""




if __name__ == "__main__":
    log = logging.getLogger()
    Scenario().run()
