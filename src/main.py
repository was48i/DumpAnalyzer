#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import stop_source
import time

from component import Component
from detection import Detection
from function import Function

parser = argparse.ArgumentParser()
parser.add_argument("--update", nargs="?", const=True, help="Update components/functions.")
parser.add_argument("--train", nargs="?", const=True, help="Training for parameter tuning.")
parser.add_argument("--compare", nargs=2, help="Compare original call stacks.")
parser.add_argument("--detect", nargs=2, help="Detect crash dump similarity.")
parser.add_argument("--stop", nargs="?", const=True, help="Count file names that can be filtered.")
args = parser.parse_args()

if __name__ == "__main__":
    # update components/functions
    if args.update:
        kdetector = Component()
        kdetector.update_component()
        kdetector = Function()
        kdetector.update_function()
    # training for parameter tuning
    if args.train:
        pass
    # compare original call stacks
    if args.compare:
        pass
    # detect crash dump similarity
    if args.detect:
        kdetector = Detection(args.detect)
        kdetector.detect_sim()
    # count filtered file names
    if args.stop:
        start = time.time()
        kdetector = stop_source.StopSource()
        kdetector.count_source()
        end = time.time()
        print(end - start)
