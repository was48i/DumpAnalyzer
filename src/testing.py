#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt

from argument import parser
from regex import find_stack
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


def compare_text(paths):
    sim = 0.0
    stack_list = []
    for path in paths:
        stack_list.append(find_stack(path))
    if stack_list[0] == stack_list[1]:
        sim = 1.0
    return sim


def pr_drawing(m_opt, n_opt):
    # get true_label and pred_score
    true_label = []
    pred_score = []
    csi_score = []
    for index, group in enumerate(data_sets[1]):
        for sample in group:
            true_label.append(index)
            pred_score.append(calculate_sim(sample, m_opt, n_opt))
            csi_score.append(compare_text(sample))
    # convert list to numpy array
    true_label = np.array(true_label)
    pred_score = np.array(pred_score)
    csi_score = np.array(csi_score)
    # get items for drawing
    precision, recall, threshold = precision_recall_curve(true_label, pred_score)
    csi_precision = precision_recall_curve(true_label, csi_score)[0]
    csi_recall = precision_recall_curve(true_label, csi_score)[1]
    ast_ap = average_precision_score(true_label, pred_score)
    csi_ap = average_precision_score(true_label, csi_score)
    # drawing
    plt.figure()
    plt.figure(figsize=(10, 10))
    plt.plot(recall, precision, color="orange", lw=2, label="Our Approach = %.3f" % ast_ap)
    plt.plot(csi_recall, csi_precision, color="gray", lw=2, label="Text Similarity = %.3f" % csi_ap)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("P-R Curve")
    plt.legend(loc="lower left")
    plt.savefig("result.svg")
    # useful tables
    np.set_printoptions(threshold=sys.maxsize)
    print(precision)
    print(recall)
    print(threshold)


if __name__ == "__main__":
    pr_drawing(0.4, 1.9)
