#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import urllib3

from compare import Compare
from detect import Detect
from stop_word import StopWord
from train import Train

parser = argparse.ArgumentParser()
parser.add_argument("--train", nargs="?", const=True, help="Training for parameter tuning.")
parser.add_argument("--stop", nargs="?", const=True, help="Count file names that can be filtered.")
parser.add_argument("--compare", nargs=2, help="Compare original call stacks.")
parser.add_argument("--detect", nargs=2, help="Detect crash dump similarity.")
args = parser.parse_args()
# suppress warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if __name__ == "__main__":
    # training for parameter tuning
    if args.train:
        Train().training()
    # count file names that can be filtered
    if args.stop:
        StopWord().count_word()
    # compare original call stacks
    if args.compare:
        Compare(args.compare).compare_dump()
    # detect crash dump similarity
    if args.detect:
        Detect(args.detect).detect_sim()
