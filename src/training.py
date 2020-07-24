#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import numpy as np

from workflow import calculate_sim
from sklearn.metrics import average_precision_score


def pr_training():
    m_opt = 0.0
    n_opt = 0.0
    ap_max = 0.0
    for m in np.arange(0.4, 0.8, 0.1):
        for n in np.arange(2.0, 12.1, 0.1):
            # get true_label and pred_score
            true_label = []
            pred_score = []
            for index, group in enumerate(data_sets):
                for pair in group:
                    true_label.append(index)
                    pred_score.append(calculate_sim(pair, m, n)[0])
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
    # load dataset
    data_sets_path = os.path.join(os.getcwd(), "json", "all_data_sets.json")
    try:
        with open(data_sets_path, "r") as fp:
            data_sets = json.load(fp)
    except FileNotFoundError:
        print("Can not find data_sets, please check.")
    # training
    pr_training()
