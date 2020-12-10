#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import time
import urllib3

from component import Component
from detect import Detect
from stop_word import StopWord

parser = argparse.ArgumentParser()
parser.add_argument("--train", nargs="?", const=True, help="Training for parameter tuning.")
parser.add_argument("--stop", nargs="?", const=True, help="Count file names that can be filtered.")
parser.add_argument("--compare", nargs=2, help="Compare original call stacks.")
parser.add_argument("--detect", nargs=2, help="Detect crash dump similarity.")
args = parser.parse_args()
# suppress warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if __name__ == "__main__":
    # training for parameter tuning
    if args.train:
        start = time.time()
        Component().update_component()
        end = time.time()
        print(end - start)
    # count filtered file names
    if args.stop:
        start = time.time()
        StopWord().count_word()
        end = time.time()
        print(end - start)
    # compare original call stacks
    if args.compare:
        pass
    # detect crash dump similarity
    if args.detect:
        start = time.time()
        Detect(args.detect).detect_sim()
        end = time.time()
        print(end - start)
