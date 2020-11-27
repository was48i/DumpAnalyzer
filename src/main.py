#!/usr/bin/env python
# -*- coding: utf-8 -*-

import component
import function
import time

from argument import parser


if __name__ == "__main__":
    args = parser.parse_args()
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
