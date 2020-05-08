#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import copy
import random

from itertools import combinations

prefix = "/dataset"


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
            if cnt % 500 == 0:
                res.append(copy.deepcopy(n_set))
                n_set.clear()
        # frequency of per increment
        distance += 1.0 / 4
        # set number of groups
        if len(res) >= 10:
            break
    return res[:10]


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
            if cnt % 500 == 0:
                res.append(copy.deepcopy(p_set))
                p_set.clear()
        # filter empty p
        p_list = [i for i in p_list if i]
        # set number of groups
        if len(res) >= 10:
            break
    return res[:10]


# def flatten(items):
#     for x in items:
#         if hasattr(x,'__iter__') and not isinstance(x, (str, bytes)):
#             yield from flatten(x)
#         else:
#             yield x


def flatten(items):
    res = []
    for group in items:
        for pair in group:
            res.append(pair)
    return res


def reshape_data():
    group_ids = range(len(os.listdir(prefix)))
    # filter single group
    group_ids = [i for i in group_ids
                 if len(os.listdir(os.path.join(prefix, str(i)))) > 1]
    n_list = []
    p_list = []
    for group_id in group_ids:
        ids = []
        pair = []
        path = os.path.join(prefix, str(group_id))
        # get dump numbers of each group
        for node in os.listdir(path):
            ids.append(node[:node.index(".")])
        prefix_ = os.path.join(prefix, str(group_id))
        # prepare list for negative sampling
        n_list.append(list(map(lambda x:
                               os.path.join(prefix_, x + ".dmp"), ids)))
        # prepare list for positive sampling
        for group in list(combinations(ids, 2)):
            pair.append(list(map(lambda x:
                                 os.path.join(prefix_, x + ".dmp"), group)))
        p_list.append(pair)
    positives = sample_positives(p_list)
    negatives = sample_negatives(n_list)
    # generate training/testing set
    res = [[flatten(negatives[:7]), flatten(positives[:7])],
           [flatten(negatives[7:]), flatten(positives[7:])]]
    # store dataset
    dst_path = os.path.join(os.getcwd(), "json", "data_sets.json")
    with open(dst_path, "w") as fp:
        json.dump(res, fp, indent=4, sort_keys=True)


if __name__ == "__main__":
    reshape_data()
