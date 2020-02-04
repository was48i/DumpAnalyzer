#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import copy
import random

from itertools import combinations


def sample_positives(p_list):
    cnt = 0
    res = []
    p_set = []
    while True:
        for p in p_list:
            # start positive sampling
            p_set.append(p.pop(0))
            cnt += 1
            # set number of samples
            if cnt % 700 == 0:
                res.append(copy.deepcopy(p_set))
                p_set.clear()
        # filter empty p
        p_list = [i for i in p_list if i]
        # set number of groups
        if len(res) >= 10:
            break
    return res[:10]


def sample_negatives(n_list):
    cnt = 0
    distance = 1.0
    res = []
    n_set = []
    while True:
        step = int(distance)
        for i in range(0, len(n_list) - step, step):
            n_set.append([random.sample(n_list[i], 1)[0],
                          random.sample(n_list[i + step], 1)[0]])
            cnt += 1
            # set number of samples
            if cnt % 700 == 0:
                res.append(copy.deepcopy(n_set))
                n_set.clear()
        # frequency of per increment
        distance += 1.0 / 4
        # set number of groups
        if len(res) >= 10:
            break
    return res[:10]


def reshape_data():
    res = []
    group_ids = range(len(os.listdir(prefix)))
    # filter single group
    group_ids = [i for i in group_ids
                 if len(os.listdir(os.path.join(prefix, str(i)))) > 1]
    p_list = []
    n_list = []
    for group_id in group_ids:
        ids = []
        pair = []
        path = os.path.join(prefix, str(group_id))
        # get dump numbers of each group
        for node in os.listdir(path):
            ids.append(node[node.index("_") + 1:])
        prefix_ = os.path.join(prefix, str(group_id))
        # prepare list for positive sampling
        for group in list(combinations(ids, 2)):
            pair.append(list(map(lambda x:
                                 os.path.join(prefix_, "dump_"+x), group)))
        p_list.append(pair)
        # prepare list for negative sampling
        n_list.append(list(map(lambda x:
                               os.path.join(prefix_, "dump_"+x), ids)))
    # generate dataset
    for p, n in zip(sample_positives(p_list), sample_negatives(n_list)):
        res.append([p, n])
    print(res)


if __name__ == "__main__":
    prefix = r"C:\DataSet"
    reshape_data()
