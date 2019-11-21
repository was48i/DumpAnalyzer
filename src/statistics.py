#!/usr/bin/env python
# -*- coding: utf-8 -*-


def matrix_stats(single_set):
    tp, fp, fn, tn = [0, 0, 0, 0]
    for p_pair in single_set[0]:
        if p_pair[0] == p_pair[1]:
            tp += 1
        else:
            fn += 1
    for n_pair in single_set[1]:
        if n_pair[0] == n_pair[1]:
            fp += 1
        else:
            tn += 1
    return tp, fp, fn, tn


def cal_metrics(single_set):
    tp, fp, fn, tn = matrix_stats(single_set)
    # calculate precision
    if tp + fp == 0:
        precision = 0
    else:
        precision = tp / (tp + fp)
    # calculate recall
    if tp + fn == 0:
        recall = 0
    else:
        recall = tp / (tp + fn)
    # calculate f1
    if precision + recall == 0:
        f1 = 0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return tuple(map(lambda x: "{:.1%}".format(x), (precision, recall, f1)))


def draw_roc(single_set):
    tp, fp, fn, tn = matrix_stats(single_set)
    # calculate TPR
    tpr = tp / (tp + fn)
    # calculate FPR
    fpr = fp / (tn + fp)
    return tpr, fpr


__all__ = [
    "cal_metrics"
]
