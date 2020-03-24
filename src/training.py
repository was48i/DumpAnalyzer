#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import Levenshtein
import numpy as np
import matplotlib.pyplot as plt

from lcs_dp import lcs_dp
from argument import parser
from regex import find_stack
from sklearn.metrics import roc_curve, auc, f1_score
from workflow import format_dump, filter_word, add_knowledge

args = parser.parse_args()
# load dataset
data_sets_path = os.path.join(os.getcwd(), "json", "data_sets.json")
try:
    with open(data_sets_path, "r") as fp:
        data_sets = json.load(fp)
except FileNotFoundError:
    print("Can't find data_sets, please check!")


def calculate_sim(paths, m, n):
    sim = 0.0
    path_1, path_2 = paths
    if args.mode == "csi":
        stack_1 = find_stack(path_1)
        stack_2 = find_stack(path_2)
        if stack_1 == stack_2:
            sim = 1.0
    else:
        above_sum = 0.0
        below_sum = 0.0
        info_1 = add_knowledge(filter_word(format_dump(path_1)))
        info_2 = add_knowledge(filter_word(format_dump(path_2)))
        components_1 = [i[0] for i in info_1]
        components_2 = [i[0] for i in info_2]
        # apply LCS
        lcs, pos_1, pos_2 = lcs_dp(components_1, components_2)
        for i, com in enumerate(lcs):
            component_sim = Levenshtein.ratio(info_1[pos_1[i]][1],
                                              info_2[pos_2[i]][1])
            above_sum += np.exp(-m * max(pos_1[i], pos_2[i])) * \
                np.exp(-n * (1 - component_sim))
        for i in range(min(len(components_1), len(components_2))):
            below_sum += np.exp(-m * i)
        sim = above_sum / below_sum
    return sim


def roc_training():
    m_opt = 0.0
    n_opt = 0.0
    auc_max = 0.0
    for m in np.arange(0.0, 2.1, 0.1):
        for n in np.arange(0.0, 2.1, 0.1):
            auc_sum = 0.0
            for group in data_sets:
                true_label = []
                pred_score = []
                positives, negatives = group
                for pos in positives:
                    true_label.append(1)
                    pred_score.append(calculate_sim(pos, m, n))
                for neg in negatives:
                    true_label.append(0)
                    pred_score.append(calculate_sim(neg, m, n))
                true_label = np.array(true_label)
                pred_score = np.array(pred_score)
                fpr = roc_curve(true_label, pred_score)[0]
                tpr = roc_curve(true_label, pred_score)[1]
                auc_score = auc(fpr, tpr)
                auc_sum += auc_score
                print("m=%.1f, n=%.1f, AUC=%.3f" % (m, n, auc_score))
            if auc_sum > auc_max:
                auc_max = auc_sum
                m_opt = m
                n_opt = n
    print(m_opt)
    print(n_opt)
    return m_opt, n_opt


def f1_training(m_opt, n_opt):
    distance_opt = 0.0
    f1_max = 0.0
    for distance in np.arange(0.5, 1.01, 0.01):
        f1_sum = 0.0
        for group in data_sets:
            true_label = []
            pred_label = []
            positives, negatives = group
            for pos in positives:
                true_label.append(1)
                if calculate_sim(pos, m_opt, n_opt) >= distance:
                    pred_label.append(1)
                else:
                    pred_label.append(0)
            for neg in negatives:
                true_label.append(0)
                if calculate_sim(neg, m_opt, n_opt) >= distance:
                    pred_label.append(1)
                else:
                    pred_label.append(0)
            f1_binary = f1_score(true_label, pred_label, average="binary")
            f1_sum += f1_binary
            print("distance=%.2f, F1 Score=%.3f" % (distance, f1_binary))
        if f1_sum > f1_max:
            f1_max = f1_sum
            distance_opt = distance
    print(distance_opt)
    return distance_opt


if __name__ == "__main__":
    roc_training()
    # f1_training(0.7, 2.0)
