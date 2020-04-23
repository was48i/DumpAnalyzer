#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt

from argument import parser
from training import calculate_sim
from sklearn.metrics import precision_recall_curve, average_precision_score

args = parser.parse_args()
# load dataset
data_sets_path = os.path.join(os.getcwd(), "json", "data_sets.json")
try:
    with open(data_sets_path, "r") as fp:
        data_sets = json.load(fp)
except FileNotFoundError:
    print("Can not find data_sets, please check.")


def pr_drawing(m_opt, n_opt):
    # get true_label and pred_score
    true_label = []
    pred_score = []
    positives, negatives = data_sets[1]
    for pos in positives:
        true_label.append(1)
        pred_score.append(calculate_sim(pos, m_opt, n_opt))
    for neg in negatives:
        true_label.append(0)
        pred_score.append(calculate_sim(neg, m_opt, n_opt))
    # convert list to numpy array
    true_label = np.array(true_label)
    pred_score = np.array(pred_score)
    # get items for drawing
    precision = precision_recall_curve(true_label, pred_score)[0]
    recall = precision_recall_curve(true_label, pred_score)[1]
    threshold = precision_recall_curve(true_label, pred_score)[2]
    ap = average_precision_score(true_label, pred_score)
    np.set_printoptions(threshold=sys.maxsize)
    # drawing
    plt.figure()
    plt.figure(figsize=(10, 10))
    plt.plot(recall, precision, color="orange", lw=2, label="AP = %.3f" % ap)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("PR Curve")
    plt.legend(loc="lower left")
    plt.savefig("csi.svg")
    # useful tables
    print(precision)
    print(recall)
    print(threshold)


if __name__ == "__main__":
    pr_drawing(0.4, 1.9)
