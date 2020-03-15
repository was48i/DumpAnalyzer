import os
import json
import math
import Levenshtein

from lcs_dp import lcs_dp
from argument import parser
from regex import find_stack
from workflow import format_dump, filter_word, add_knowledge

args = parser.parse_args()
# load dataset
data_sets_path = os.path.join(os.getcwd(), "json", "data_sets.json")
try:
    with open(data_sets_path, "r") as f:
        data_sets = json.load(f)
except FileNotFoundError:
    print("Can't find data_sets, please check!")


def get_pair(paths):
    pair = []
    # convert paths to pair
    for path in paths:
        if args.mode == "ast":
            if not args.raw:
                item = add_knowledge(filter_word(format_dump(path)))
            else:
                item = add_knowledge(format_dump(path))
        else:
            item = find_stack(path)
        pair.append(item)
    return pair


def cal_sim(paths):
    dup = 0
    path_1, path_2 = paths
    if args.mode == "ast":
        info_1 = add_knowledge(filter_word(format_dump(path_1)))
        info_2 = add_knowledge(filter_word(format_dump(path_2)))
        coms_1 = [i[0] for i in info_1]
        coms_2 = [i[0] for i in info_2]
        above_sum = 0
        below_sum = 0
        lcs, pos_1, pos_2 = lcs_dp(coms_1, coms_2)
        for i, com in enumerate(lcs):
            com_sim = Levenshtein.ratio(info_1[pos_1[i]][1],
                                        info_2[pos_2[i]][1])
            above = math.exp(-8 * max(pos_1[i], pos_2[i])) * \
                math.exp(-8 * (1 - com_sim))
            above_sum += above
        for i in range(max(len(coms_1), len(coms_2))):
            below_sum += math.exp(-8 * i)
        sim = above_sum / below_sum
        if sim >= 0.5:
            dup = 1
    else:
        info_1 = find_stack(path_1)
        info_2 = find_stack(path_2)
        if info_1 == info_2:
            dup = 1
    return dup


def matrix_stats(group):
    positives, negatives = group
    tp, fp, fn, tn = [0, 0, 0, 0]
    # count positive samples
    for dup in positives:
        if dup == 1:
            tp += 1
        else:
            fn += 1
    # count negative samples
    for dup in negatives:
        if dup == 1:
            fp += 1
        else:
            tn += 1
    return tp, fp, fn, tn


def cal_metrics(group):
    tp, fp, fn, tn = matrix_stats(group)
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
    return tuple(map(lambda x: "{:.3f}".format(x), (precision, recall, f1)))


def validate():
    precisions = []
    recalls = []
    f1s = []
    for group in data_sets:
        trans_group = []
        positives = []
        negatives = []
        # get positive pair
        for p_paths in group[0]:
            dup = cal_sim(p_paths)
            positives.append(dup)
        trans_group.append(positives)
        # get negative pair
        for n_paths in group[1]:
            dup = cal_sim(n_paths)
            negatives.append(dup)
        trans_group.append(negatives)
        # calculate metrics
        precision, recall, f1 = cal_metrics(trans_group)
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)
    return precisions, recalls, f1s


__all__ = [
    "validate"
]
