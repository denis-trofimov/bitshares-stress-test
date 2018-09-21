#!/usr/bin/python
# -*- coding: UTF-8 -*-
""" Scenario test, stress test tool for BitShares based on JSON and pybitshares.
"""

# Since simplejson is backwards compatible, you should feel free to import
# it as `json`
import simplejson as json
import logging
import argparse
import time
import pprint
from collections import OrderedDict
from functools import wraps
from bitshares import BitShares
from bitshares.block import Block
from bitshares.blockchain import Blockchain
from bitshares.proposal import Proposals
from bitshares.account import Account
from grapheneapi.exceptions import RPCError
from bitsharesapi.exceptions import UnhandledRPCError


logging.basicConfig(
    format='%(created)f - %(levelname)s - %(funcName)s - %(message)s',
    level=logging.INFO,
    filename='benchmark.log',
)
log = logging.getLogger()


def log_exceptions(func):
    """ Decorator to put exceptions in called `func` to log."""
    @wraps(func)
    def function_wrapper(*args: list, **kwargs: dict):
        """ Wrapper of log_exceptions."""
        try:
            result = func(*args, **kwargs)
        except (RPCError,  UnhandledRPCError) as err:
            result = {"message": str(err)}
        return result
    return function_wrapper


class Scenario(object):

    """ Scenario test, stress test tool for BitShares based on JSON and
        pybitshares.
    """

    def __init__(self, script_name: str ="scenario.json"):
        self.roundup: dict = {}
        try:
            with open(script_name, 'rt') as file:
                self.scenario: list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as err:
            log.critical(
                'Fail to open and parse scenario file "{0}" due to {1}.'.format(
                    script_name, err)
            )
        log.info(
            'Start processing of scenario file "{0}".'.format(script_name)
        )
        for node_call in self.scenario:
            NodeCalls(node_call, self.roundup).run()
        log.info(
            'Finish processing of scenario file "{0}".'.format(script_name)
        )
        log.info('Track time spent on calls, sum up to roundup table')
        log.info(pprint.pformat(self.roundup))


class NodeCalls(object):

    """ Connect to a specified node and perform calls."""

    def __init__(self, scenario: dict, roundup: dict):
        self.scenario: dict = scenario
        self.roundup = roundup

    def connect(self, node: str, **kwargs):
        """ Connect to a specified node."""
        self.bts = BitShares(node, kwargs)
        log.info('Connected to node "{0}".'.format(self.bts.rpc.url))
        if not getattr(self, 'chain', None):
            self.chain = Blockchain(blockchain_instance=self.bts)

    def run(self):
        try:
            self.connect(self.scenario.get("node"))
        except BaseException as err:
            log.critical('Fail to connect to node "{0} due to {1}".'.format(
                self.scenario.get("node"), err)
            )
            log.error('Scenario run has stopped.')
            return

        if not self.scenario or not self.scenario.get("stages", []):
            log.warning("Empty stages!")

        for stage in self.scenario.get("stages", []):
            start_time = time.time()
            method: str = stage.get("method", '')
            call = getattr(self, method, lambda: None)
            # Copy method from call to responce.
            result: dict = {"method": method}
            if not method or not call:
                result['result']['message']: str = ""
                "`{0}` is not implemented!".format(method)
                log.error(json.dumps(result))
                continue
            else:
                kwargs: dict = stage.get("params", {})
                try:
                    result['result']: str = call(**kwargs)
                    log.info(json.dumps(result))
                except (RPCError,  UnhandledRPCError) as err:
                    result['result']['message']: str = str(err)
                    log.error(json.dumps(result))
            # Track time spent on calls, sum up to table
            self.roundup[method] = self.roundup.get(method, 0) + time.time() - start_time

    def get_global_properties(self):
        """ Retrieve the current global_property_object."""
        return self.bts.info()

    def get_block(self, block_num: int):
        """ Retrieve a full, signed block."""
        return Block(block_num, blockchain_instance=self.bts, lazy=False)

    def get_chain_properties(self):
        """ Retrieve the chain_property_object associated with the chain."""
        return self.chain.get_chain_properties()

    def get_dynamic_global_properties(self):
        """ This call returns the *dynamic global properties*."""
        return self.chain.info()

    def get_config(self):
        """ Retrieve compile-time constants."""
        return self.chain.config()

#    def get_all_accounts(self, start='', stop='', steps=1e3, **kwargs):
#        """ Yields account names between start and stop.
#
#            :param str start: Start at this account name
#            :param str stop: Stop at this account name
#            :param int steps: Obtain ``steps`` ret with a single call from RPC
#        """
#        return json.dumps((account for account in self.chain.get_all_accounts(
#            start, stop,  steps)), iterable_as_array=True)

    def get_accounts(self, account_ids: list) -> list:
        """ Get a list of accounts by ID.

            :param str account_ids: Identify of the account
            :param bitshares.bitshares.BitShares blockchain_instance: BitShares
                   instance
            :returns: Account data list
            :rtype: list
            :raises bitshares.exceptions.AccountDoesNotExistsException: if account
                    does not exist

        """
        result = []
        for account_id in account_ids:
            account = Account(account_id,  blockchain_instance=self.bts)
            result.append(account)
        return result

    def get_chain_id(self):
        """ Get the chain ID."""
        return {"chain_id": self.chain.get_chain_properties()["chain_id"]}

    @log_exceptions
    def get_transaction(self, block_num: int, trx_in_block: int):
        """ Fetch an individual processed transaction from a block."""
        return self.bts.rpc.get_transaction(block_num, trx_in_block)

    def get_proposed_transactions(self, account: str):
        """ Obtain a list of pending proposals for an account.

            :param str account: Account name
            :param bitshares blockchain_instance: BitShares() instance to use
                when accesing a RPC

        """
        proposals: list = Proposals(account,  blockchain_instance=self.bts)
        return {"proposed_transactions": proposals}

#    def get_transaction(self, block_num: int, trx_in_block: int):
#        """processed_transaction graphene::app::database_api::get_transaction(uint32_t block_num, uint32_t trx_in_block) const
#        used to fetch an individual transaction."""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",   dest='daemon', help="run as daemon and loop scenario execution"
    )
    parser.add_argument('file', help="scenario JSON file")
    args = parser.parse_args()
    Scenario(args.file)
