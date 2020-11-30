#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import component
import function
import time

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--update", nargs="?", const=True, help="Update components/functions.")
parser.add_argument("-t", "--train", nargs="?", const=True, help="Training for parameter tuning.")
parser.add_argument("-c", "--compare", nargs=2, help="Compare original call stacks.")
parser.add_argument("-d", "--detect", nargs=2, help="Detect crash dump similarity.")
args = parser.parse_args()

if __name__ == "__main__":
    # update components/functions
    if args.update:
        start = time.time()
        cpnt = component.Component()
        cpnt.update_component()
        func = function.Function()
        func.update_function()
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
        pass
