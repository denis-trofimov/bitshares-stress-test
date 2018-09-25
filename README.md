# Scenario tester, stress test tool for BitShares based on JSON and pybitshares.

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

### Usage command line help:
```sh
$ python3 loop_scenario.py -h
usage: loop_scenario.py [-h] [-d DAEMON] file

positional arguments:
  file        scenario JSON file

optional arguments:
  -h, --help  show this help message and exit
  -d DAEMON   run as daemon and loop scenario execution
```

### Example scenario script in the JSON format [loop_scenario.json](loop_scenario.json).

## License

A copy of the license is available in the repository's
[LICENSE](LICENSE) file.
