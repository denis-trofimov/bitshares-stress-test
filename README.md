# Scenario tester, stress test tool for BitShares based on python-bitshares.

---

## Installation

### Install dependancies:
    $ sudo apt-get install -y -qq libffi-dev libssl-dev python-dev python3-dev python3-pip
    $ pip3 install -q bitshares requests simplejson
    or
    $ pip3 install -r requirements.txt

### Clone repository:
    $ git clone https://github.com/denis-trofimov/bitshares-stress-test.git

## Usage
#### Scenario tester
    $ cd bitshares-stress-test
    $ python3 loop_scenario.py loop_scenario.json
    $ python3 loop_scenario.py -c 6 -r 100 loop_scenario.json
    $ python3 loop_scenario.py -d loop_scenario.json

### Usage command line help:
```sh
$ python3 loop_scenario.py -h
usage: loop_scenario.py [-h] [-r ROUNDS] [-c CONNECTIONS] [-d] filename

positional arguments:
  filename        scenario JSON file

optional arguments:
  -h, --help      show this help message and exit
  -r ROUNDS       number of scenario execution loops
  -c CONNECTIONS  number of concurrent connections
  -d              run as daemon and loop scenario execution
```

### Example scenario script in the JSON format [loop_scenario.json](loop_scenario.json).

## License

A copy of the license is available in the repository's
[LICENSE](LICENSE) file.

---

# Recent activity

* [Report](report.md) on tcpkali test usage concerning [Test connection limit to "ws://hawking.array.io:8090" not using python websocket libs. #19](https://github.com/denis-trofimov/bitshares-stress-test/issues/19)
* Achived up to 2888 TPS on get random block operation.
