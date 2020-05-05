#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
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
    # set figure
    plt.figure()
    plt.figure(figsize=(10, 10), dpi=600)
    plt.plot(recall, precision, color="orange", label="Our Approach = %.3f" % ast_ap)
    plt.plot(csi_recall, csi_precision, color="gray", label="Text Similarity = %.3f" % csi_ap)
    # grid drawing
    plt.minorticks_on()
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.grid(which="both", axis="y", linestyle='--', alpha=0.5)
    plt.grid(which="major", axis="x", linestyle='--', alpha=0.5)
    # annotate cut point
    for i, p in enumerate(precision):
        if p >= 0.95:
            x = recall[i]
            y = precision[i]
            distance = threshold[i]
            plt.plot(x, y, color="red", marker=".")
            plt.annotate("(%.3f, %.3f)\nthreshold = %.3f" % (x, y, distance), xy=(x, y),
                         xytext=(5, 5), textcoords='offset points')
            break
    # add useful words
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.legend(loc="lower left")
    plt.savefig("result.png")


if __name__ == "__main__":
    pr_drawing(0.4, 1.9)
