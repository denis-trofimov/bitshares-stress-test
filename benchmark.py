#!/usr/bin/python
# -*- coding: UTF-8 -*-
""" Scenario test, stress test tool for BitShares based on JSON and pybitshares.
    get_block, get_transaction, get_chain_properties, get_global_properties, get_config, get_chain_id, get_dynamic_global_properties, get_accounts
"""


#import json
# Since simplejson is backwards compatible, you should feel free to import
# it as `json`
import simplejson as json
import logging
from bitshares import BitShares
from bitshares.block import Block, BlockHeader
from bitshares.blockchain import Blockchain


class Scenario(object):
    """ Scenario test, stress test tool for BitShares based on JSON and
        pybitshares.
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
        self.bts = BitShares(
            "ws://newton.array.io:8090", nobroadcast=True, debug=True)
        print('Connected to node "{0}".'.format(self.bts.rpc.url))

        for stage in self.scenario.get("stages", []):
            kwargs: dict = stage.get("params", {})
            result: str = getattr(self, stage.get("method", ''), lambda:None)(**kwargs)
            # Copy method from call to responce.
            if result:
                if isinstance(result, dict):
                    result["method"] = stage.get("method", '')
                    print(json.dumps(result))
                else:
                    print(result)
            else:
                print("The method `{0}` is not implemented!".format(stage.get("method", '')))

    def get_global_properties(self):
        """ Retrieve the current global_property_object."""
        return self.bts.info()

    def get_block(self, block_num: int):
        """ Retrieve a full, signed block."""
        return Block(block_num, blockchain_instance=self.bts, lazy=False)

    def get_chain_properties(self):
        """ Retrieve the chain_property_object associated with the chain."""
        self.chain = Blockchain(mode="head", blockchain_instance=self.bts)
        print("Identify the network parameters: {0}".format(
            self.chain.get_network()))
        return self.chain.get_chain_properties()

    def get_dynamic_global_properties(self):
        """ This call returns the *dynamic global properties*
        """
        return self.chain.info()

    def get_config(self):
        """ Retrieve compile-time constants."""

    def get_accounts(self, start='', stop='', steps=1e3, **kwargs):
        """ Yields account names between start and stop.

            :param str start: Start at this account name
            :param str stop: Stop at this account name
            :param int steps: Obtain ``steps`` ret with a single call from RPC
        """
        return json.dumps((account for account in self.chain.get_all_accounts(
            start, stop,  steps)), iterable_as_array=True)

    def get_chain_id(self):
        """ Get the chain ID."""
        return {"chain_id": self.chain.get_chain_properties()["chain_id"]}

#    def get_transaction(self, block_num: int, trx_in_block: int):
#        """processed_transaction graphene::app::database_api::get_transaction(uint32_t block_num, uint32_t trx_in_block) const
#        used to fetch an individual transaction."""


if __name__ == "__main__":
    log = logging.getLogger()
    Scenario().run()
