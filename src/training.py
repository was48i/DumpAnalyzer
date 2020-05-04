#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import Levenshtein
import numpy as np

from lcs_dp import lcs_dp
from argument import parser
from sklearn.metrics import average_precision_score
from workflow import format_dump, filter_word, add_knowledge

args = parser.parse_args()
# load dataset
data_sets_path = os.path.join(os.getcwd(), "json", "data_sets.json")
try:
    with open(data_sets_path, "r") as fp:
        data_sets = json.load(fp)
except FileNotFoundError:
    print("Can not find data_sets, please check.")


def calculate_sim(paths, m, n):
    sim = 0.0
    # prepare items for calculation
    info_list = []
    component_list = []
    for path in paths:
        if not args.raw:
            info = add_knowledge(filter_word(format_dump(path)))
        else:
            info = add_knowledge(format_dump(path))
        info_list.append(info)
        component_list.append([i[0] for i in info])
    # calculate similarity
    above_sum = 0.0
    below_sum = 0.0
    # apply LCS
    lcs, x_pos, y_pos = lcs_dp(component_list)
    for i, com in enumerate(lcs):
        component_sim = Levenshtein.ratio(info_list[0][x_pos[i]][1], info_list[1][y_pos[i]][1])
        above_sum += np.exp(-m * max(x_pos[i], y_pos[i])) * np.exp(-n * (1 - component_sim))
    for i in range(max(len(component_list[0]), len(component_list[1]))):
        below_sum += np.exp(-m * i)
    sim = above_sum / below_sum
    return sim


def pr_training():
    m_opt = 0.0
    n_opt = 0.0
    ap_max = 0.0
    for m in np.arange(0.0, 2.1, 0.1):
        for n in np.arange(0.0, 2.1, 0.1):
            # get true_label and pred_score
            true_label = []
            pred_score = []
            positives, negatives = data_sets[0]
            for pos in positives:
                true_label.append(1)
                pred_score.append(calculate_sim(pos, m, n))
            for neg in negatives:
                true_label.append(0)
                pred_score.append(calculate_sim(neg, m, n))
            true_label = np.array(true_label)
            pred_score = np.array(pred_score)
            # calculate ap
            ap = average_precision_score(true_label, pred_score)
            print("m=%.1f, n=%.1f, AP=%.3f" % (m, n, ap))
            # get optimal value
            if ap > ap_max:
                ap_max = ap
                m_opt = m
                n_opt = n
    print(m_opt)
    print(n_opt)


if __name__ == "__main__":
    pr_training()
