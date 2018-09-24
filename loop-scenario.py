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
from collections import OrderedDict
from functools import wraps
from bitshares import BitShares
from bitshares.block import Block
from bitshares.blockchain import Blockchain
from bitshares.proposal import Proposals
from bitshares.account import Account
from grapheneapi.exceptions import RPCError
from bitsharesapi.exceptions import UnhandledRPCError


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
                self.scenario: dict = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as err:
            log.critical(
                'Fail to open and parse scenario file "{0}" due to {1}.'.format(
                    script_name, err)
            )
        log.info(
            'Start processing of scenario file "{0}".'.format(script_name)
        )
        for node_call in self.scenario.get("scenarios", []):
            NodeCalls(node_call, self.roundup).run()
        log.info(
            'Finish processing of scenario file "{0}".'.format(script_name)
        )
        log.info('Track time spent on calls, sum up to roundup table')
        log.info(json.dumps(self.roundup,  indent=(2 * ' ')))


class NodeCalls(object):
    """ Connect to a specified node and perform calls."""

    def __init__(self, scenario: dict, roundup: dict):
        self.scenario: dict = scenario
        self.node = self.scenario.get("node")
        self.cycles: int =  self.scenario.get("cycles",  0)
        self.workers: int =  self.scenario.get("workers",  0)
        self.time_limit: int =  self.scenario.get("time_limit",  0)
        self.roundup = roundup

    def prepare_calls_sequence(self):
        """ Create calls sequence from a script for node.

            :returns calls_list     The elements of the iterable are expected to
            be iterables that are unpacked as arguments.
        """
        self.calls_list = []
        for stage in self.scenario.get("stages", []):
            method: str = stage.get("method", '')
            call = getattr(self, method, lambda: None)
            self.calls_list.append((call, method,  stage.get("params", {})))

    def generate_cycled_call_sequence(self):
        """Generate cycles of each node_call."""
        for iteration in range(self.cycles):
            for call in self.calls_list:
                yield call

    def run(self):
        """ Prepare and run loop for single node in scenarios."""
        self.prepare_calls_sequence()
        for args in self.generate_cycled_call_sequence():
            """ Make single call from calls list."""
            Call(self.node).call_wrapper(args[0], args[1], args[2])

    @staticmethod
    def make_call(args: tuple):
        """ Make single call from calls list."""
        Call(args[0]).call_wrapper(args[1], args[2], args[3])


class Call():
    """ Concurent call a method for node."""
    def __init__(self, node: str):
        """ Connect to a specified node."""
        self.bts = BitShares(node)

    def call_wrapper(self, call, method: str, kwargs: dict):
        # Copy method from call to responce.
        result: dict = {"method": method}
        if not method or not call:
            result['result']['message']: str = ""
            "`{0}` is not implemented!".format(method)
#            log.error(json.dumps(result,  indent=(2 * ' ')))
        else:
            try:
                result['result']: str = call(**kwargs)
#                log.info(json.dumps(result,  indent=(2 * ' ')))
            except (RPCError,  UnhandledRPCError) as err:
                result['result']['message']: str = str(err)
#                log.error(json.dumps(result,  indent=(2 * ' ')))
        return result

    def get_global_properties(self):
        """ Retrieve the current global_property_object."""
        return self.bts.info()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",   dest='daemon', help="run as daemon and loop scenario execution"
    )
    parser.add_argument('file', help="scenario JSON file")
    args = parser.parse_args()

    logging.basicConfig(
        format='%(created)f - %(levelname)s - %(funcName)s - %(message)s',
        level=logging.INFO,
        filename='scenario.log',
    )
    log = logging.getLogger()

    Scenario(args.file)
