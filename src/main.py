#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import time
import urllib3

from component import Component
from detect import Detect
from function import Function
from stop_word import StopWord

parser = argparse.ArgumentParser()
parser.add_argument("--update", nargs="?", const=True, help="Update components/functions.")
parser.add_argument("--train", nargs="?", const=True, help="Training for parameter tuning.")
parser.add_argument("--compare", nargs=2, help="Compare original call stacks.")
parser.add_argument("--detect", nargs=2, help="Detect crash dump similarity.")
parser.add_argument("--stop", nargs="?", const=True, help="Count file names that can be filtered.")
args = parser.parse_args()

if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # update components/functions
    if args.update:
        start = time.time()
        Component().update_component()
        Function().update_function()
        end = time.time()
        print(end - start)
    # training for parameter tuning
    if args.train:
        pass
    # compare original call stacks
    if args.compare:
        pass
    # detect crash dump similarity
    if args.detect:
        start = time.time()
        Detect(args.detect).detect_sim()
        end = time.time()
        print(end - start)
    # count filtered file names
    if args.stop:
        start = time.time()
        StopWord().count_word()
        end = time.time()
        print(end - start)
