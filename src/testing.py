#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import Levenshtein
import numpy as np
import matplotlib.pyplot as plt

from argument import parser
from regex import find_stack
from training import calculate_sim
from workflow import format_dump, filter_word, add_knowledge
from sklearn.metrics import precision_recall_curve, average_precision_score

args = parser.parse_args()
# load dataset
data_sets_path = os.path.join(os.getcwd(), "json", "data_sets.json")
try:
    with open(data_sets_path, "r") as fp:
        data_sets = json.load(fp)
except FileNotFoundError:
    print("Can not find data_sets, please check.")


def edit_distance(paths):
    sim = 0.0
    stack = []
    for path in paths:
        stack.append(find_stack(path))
    if stack[0] == stack[1]:
        sim = 1.0
    return sim


def prefix_match(paths):
    prefix = []
    for path in paths:
        info = add_knowledge(filter_word(format_dump(path)))
        prefix.append(info[0][1])
    sim = Levenshtein.ratio(prefix[0], prefix[1])
    return sim


def pr_drawing(m_opt, n_opt):
    # get true_label and pred_score
    true_label = []
    pred_score = []
    ed_score = []
    pm_score = []
    for index, group in enumerate(data_sets[1]):
        for pair in group:
            true_label.append(index)
            pred_score.append(calculate_sim(pair, m_opt, n_opt)[0])
            ed_score.append(edit_distance(pair))
            pm_score.append(prefix_match(pair))
    # convert list to numpy array
    true_label = np.array(true_label)
    pred_score = np.array(pred_score)
    ed_score = np.array(ed_score)
    pm_score = np.array(pm_score)
    # get items for drawing
    precision, recall, threshold = precision_recall_curve(true_label, pred_score)
    precision_ed = precision_recall_curve(true_label, ed_score)[0]
    precision_pm = precision_recall_curve(true_label, pm_score)[0]
    recall_ed = precision_recall_curve(true_label, ed_score)[1]
    recall_pm = precision_recall_curve(true_label, pm_score)[1]
    ap = average_precision_score(true_label, pred_score)
    ap_ed = average_precision_score(true_label, ed_score)
    ap_pm = average_precision_score(true_label, pm_score)
    # set figure
    plt.figure()
    plt.figure(figsize=(10, 10), dpi=600)
    plt.plot(recall, precision, color="#F0AB00", label="Our Approach = %.3f" % ap)
    plt.plot(recall_pm, precision_pm, color="#008FD3", label="Prefix Match = %.3f" % ap_pm)
    plt.plot(recall_ed, precision_ed, color="#666666", label="Edit Distance = %.3f" % ap_ed)
    # grid drawing
    plt.minorticks_on()
    plt.xlim([0.0, 1.0])
    plt.ylim([0.5, 1.02])
    plt.grid(which="both", axis="y", linestyle="--", alpha=0.5)
    plt.grid(which="major", axis="x", linestyle="--", alpha=0.5)
    # annotate cut point
    # for i, p in enumerate(precision):
    #     if p >= 0.950:
    #         x = recall[i]
    #         y = precision[i]
    #         distance = threshold[i]
    #         plt.plot(x, y, color="#E35500", marker=".")
    #         plt.annotate("(%.3f, %.3f)\nthreshold = %.4f" % (x, y, distance), xy=(x, y),
    #                      xytext=(5, 5), textcoords="offset points")
    #         break
    # add useful words
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.legend(loc="lower left")
    plt.savefig("result.png")


if __name__ == "__main__":
    pr_drawing(0.4, 1.9)
