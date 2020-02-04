import os
import json

from argument import parser
from workflow import find_key
from regex import find_backtrace, find_stack

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
        with open(path, "r", encoding="ISO-8859-1") as fp:
            file_text = fp.read()
        if args.mode == "ast":
            item = find_key(find_backtrace(file_text))[1]
            if find_key(find_backtrace(file_text))[0] == "":
                print(path)
        else:
            item = find_stack(file_text)
        pair.append(item)
    return pair


def matrix_stats(group):
    positives, negatives = group
    tp, fp, fn, tn = [0, 0, 0, 0]
    # count positive samples
    for p_pair in positives:
        if p_pair[0] == p_pair[1]:
            tp += 1
        else:
            fn += 1
    # count negative samples
    for n_pair in negatives:
        if n_pair[0] == n_pair[1]:
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
    return tuple(map(lambda x: "{:.2%}".format(x), (precision, recall, f1)))


def validate():
    precisions = []
    recalls = []
    f1s = []
    for group in data_sets:
        trans_group = []
        positives = []
        negatives = []
        # get positives' pair
        for p_paths in group[0]:
            p_pair = get_pair(p_paths)
            positives.append(p_pair)
        trans_group.append(positives)
        # get negatives' pair
        for n_paths in group[1]:
            n_pair = get_pair(n_paths)
            # for debug
            # if n_pair[0] == n_pair[1]:
            #     print(n_paths)
            negatives.append(n_pair)
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
