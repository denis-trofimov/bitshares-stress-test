#!/usr/bin/python
# -*- coding: UTF-8 -*-
""" Scenario test, stress test tool for BitShares based on JSON and pybitshares.
"""

# Since simplejson is backwards compatible, you should feel free to import
# it as `json`
import simplejson as json
import csv
import logging
import argparse
import time
import itertools
import os
from multiprocessing import Pool, TimeoutError, Process, Queue, JoinableQueue
from functools import wraps
from bitshares import BitShares
from bitshares.block import Block
from bitshares.blockchain import Blockchain
from bitshares.account import Account
from grapheneapi.exceptions import RPCError
from bitsharesapi.exceptions import UnhandledRPCError


sentinel = -1
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

    def save_csv(self):
        file_name = "node_performance.csv"
        fields = self.node_rows[0].keys()
        exist_file = os.path.isfile(file_name)
        with open(file_name,  "a") as file:
           writer = csv.DictWriter(file, fields, quoting=csv.QUOTE_ALL)
           if not exist_file:
               writer.writeheader()
           writer.writerows(self.node_rows)

    def __init__(self, script_name: str ="scenario.json"):
        self.node_rows: list = []

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
            NodeSequence(node_call, self.node_rows).run_workers()
        log.info(
            'Finish processing of scenario file "{0}".'.format(script_name)
        )
        log.info('Track time spent on calls, sum up to node_rows table')

        self.save_csv()
        log.info(json.dumps(self.node_rows,  indent=(2 * ' ')))


def make_call(*args: tuple):
    """ Make single call from calls list."""
    time.sleep(0.5)  # 100ms
    return NodeCall(args[0]).call_wrapper(args[1], args[2], args[3])

def creator(workers: int , data,  queue_calls: Queue):
    """
    Creates data to be consumed and waits for the consumer
    to finish processing
    """
    print('Creating data and putting it on the queue')
    for item in data:
        queue_calls.put(item)
    # send termination sentinel, one for each process
    for i in range(workers):
        queue_calls.put(sentinel)
    print(f'Creating send termination sentinels, one for each of {workers}'
    ' process and putting it on the queue')


def worker(node: str, worker_name: str, queue_calls: Queue, queue_error: Queue, queue_success: Queue):
    """ Consumes some data from queue_calls and works on it."""
    connection = NodeCall(node)
    counter = 0
    start = time.perf_counter()
    print("Started worker {0}!".format(worker_name))
    for args in iter(queue_calls.get, sentinel):
        queue_calls.task_done()
        counter += 1
#        print("Worker {0} got {1} args.".format(worker_name, args))
        result = connection.call_wrapper(*args)
        stop = time.perf_counter()
        if isinstance(result, dict) and result.get('error', ''):
            queue_error.put(result)
        else:
            queue_success.put({args[1]: stop - start})
        start = stop

    print("Worker {0} done {1} jobs.".format(worker_name, counter))
    queue_calls.task_done()
    print(f"{queue_calls.qsize()} the approximate size of the queue.")




class NodeSequence(object):

    """ Connect to a specified node and perform calls."""

    def __init__(self, scenario: dict, node_rows: list):
        self.scenario: dict = scenario
        self.node = self.scenario.get("node")
        self.cycles: int = self.scenario.get("cycles",  1)
        self.workers: int = self.scenario.get("workers",  1)
        self.time_limit: int = self.scenario.get("time_limit",  20)
        self.node_rows = node_rows

    def prepare_calls_sequence(self):
        """ Create calls sequence from a script for node.

            :returns calls_list     The elements of the iterable are expected to
            be iterables that are unpacked as arguments.

        """
        self.calls_list = []
        for stage in self.scenario.get("stages", []):
            method: str = stage.get("method", '')
            call = getattr(NodeCall, method, lambda: None)
            self.calls_list.append((call, method,  stage.get("params", {})))
#             self.calls_list.append((self.node, call, method,  stage.get("params", {})))

    def generate_cycled_call_sequence(self):
        """Generate cycles of each node_call."""
        for iteration in range(self.cycles):
            for call in self.calls_list:
                yield call

    def run_workers(self):
        """ Prepare and run loop for single node in scenarios."""
        self.prepare_calls_sequence()
        start_time = time.perf_counter()
        run_info = {}
        methods_times= {}
        errors = []
        successes = 0

        queue_calls = JoinableQueue()
        queue_error = Queue()
        queue_success = Queue()
        processes = []
        process = Process(
            daemon=False, target=creator,
            args=(self.workers, self.generate_cycled_call_sequence(), queue_calls)
        )
        process.start()
        processes.append(process)
        for index in range(self.workers):
            worker_name = f"worker-{index}"
            process = Process(
                daemon=False, target=worker,
                args=(self.node, worker_name, queue_calls, queue_error, queue_success)
            )
            processes.append(process)
            process.start()

        print(f"Before join {queue_calls.qsize()} the approximate size of the queue.")
        queue_calls.join()
        for process in processes:
            process.join()
        print(f"After join {queue_calls.qsize()} the approximate size of the queue.")

        #  send termination sentinel, one for each process
        queue_error.put(None)
        queue_success.put(None)
        for method_time in iter(queue_success.get, None):
            for method_name, time_value in method_time.items():
                methods_times[method_name] = (
                    methods_times.get(method_name, 0) + time_value)
            successes += 1
        for message in iter(queue_error.get, None):
            errors.append(message)

        # Track time spent on calls, sum up to table
        run_info['node'] = self.node
        run_info['cycles'] = self.cycles
        run_info['workers'] = self.workers
        run_info['success'] = run_info.get('success', 0) + successes
        run_info['errors'] = run_info.get('errors', 0) + len(errors)
        run_info['time_limit'] = self.time_limit
        run_info['time'] = run_info.get('time', 0) + time.perf_counter() - start_time
        if run_info['time']:
            run_info['TPS'] = float(run_info['success']) / run_info['time']
            sum_calls_time = sum(methods_times.values())
            for method_name, time_value in methods_times.items():
                run_info[method_name] = 100 * time_value / sum_calls_time
#                run_info[method_name] = time_value
        else:
            run_info['TPS'] = 'undefined'
        self.node_rows.append(run_info)

        log.error(json.dumps(errors,  indent=(2 * ' ')))

    def run(self):
        """ Prepare and run loop for single node in scenarios."""
        self.prepare_calls_sequence()
        start_time = time.time()
        run_info = {}
        success = []
        errors = []
        successes = 0
        with Pool(processes=self.workers) as pool:
            """ starmap_async(func, iterable[, chunksize[, callback[,
                error_callback]]])
                A combination of starmap() and map_async() that iterates over
                iterable of iterables and calls func with the iterables unpacked.
                Returns a result object.
                """
            multiple_results = pool.starmap_async(
                make_call, self.generate_cycled_call_sequence(),  self.workers,
                success.append, errors.append)

            for result in multiple_results.get(timeout=2):
#                log.info(json.dumps(result,  indent=(2 * ' ')))

                message = result.get('error', '')
                if message:
                    errors.append(result)
                else:
                    successes += 1

            # Track time spent on calls, sum up to table
            run_info['node'] = self.node
            run_info['cycles'] = self.cycles
            run_info['workers'] = self.workers
            run_info['success'] = run_info.get('success', 0) + successes
            run_info['errors'] = run_info.get('errors', 0) + len(errors)
            run_info['time_limit'] = self.time_limit
            run_info['time'] = run_info.get('time', 0) + time.time() - start_time
            if run_info['time']:
                run_info['TPS'] = float(run_info['success']) / run_info['time']
            else:
                run_info['TPS'] = 'undefined'
            self.node_rows.append(run_info)

            log.error(json.dumps(errors,  indent=(2 * ' ')))


class NodeCall():

    """ Concurent call a method for node."""

    def __init__(self, node: str):
        """ Connect to a specified node."""
        self.bts = BitShares(node)

    def call_wrapper(self, call, method: str, kwargs: dict):
        # Copy method from call to responce.
        result: dict = {"method": method}
        if not method or not call:
            result['error']: str = ""
            "`{0}` is not implemented!".format(method)
        else:
            try:
                # call can return dict, list, str
                result['result'] = call(self, **kwargs)
            except (RPCError,  UnhandledRPCError) as err:
                result['error']: str = str(err)
        return result

    def get_global_properties(self):
        """ Retrieve the current global_property_object."""
        return self.bts.info()

    def get_block(self, block_num: int):
        """ Retrieve a full, signed block."""
        result = Block(block_num, blockchain_instance=self.bts)
        return dict(result)

    def get_chain_properties(self):
        """ Retrieve the chain_property_object associated with the chain."""
        self.chain = Blockchain(blockchain_instance=self.bts)
        return self.chain.get_chain_properties()

    def get_dynamic_global_properties(self):
        """ This call returns the *dynamic global properties*."""
        self.chain = Blockchain(blockchain_instance=self.bts)
        return self.chain.info()

    def get_config(self):
        """ Retrieve compile-time constants."""
        self.chain = Blockchain(blockchain_instance=self.bts)
        return self.chain.config()

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
            result.append(dict(account))
        return result

    def get_chain_id(self):
        """ Get the chain ID."""
        self.chain = Blockchain(blockchain_instance=self.bts)
        return self.chain.get_chain_properties()

    def get_transaction(self, block_num: int, trx_in_block: int):
        """ Fetch an individual processed transaction from a block."""
        result = self.bts.rpc.get_transaction(block_num, trx_in_block)
        return dict(result)


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
