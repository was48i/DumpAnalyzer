#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import bugzilla
import union_find


def group_dumps(bugs):
    path_map = dict()
    pair_list = []
    ex_dumps = []
    result = []
    # use bugzilla api
    url = "https://hdbits.wdf.sap.corp/bugzilla/rest/"
    b = bugzilla.Bugzilla(url=url,
                          api_key="MloWmOsYyaYqLCfxFA8r3y6bRCENwJYhlranhUWh")
    for bug_id in bugs:
        bug = b.get_bug(bug_id)
        child = b.get_bug(bug.dupe_of)
        # add to pair if necessary
        if child.cf_crashdump_location:
            path_map[bug_id] = bug.cf_crashdump_location
            path_map[bug.dupe_of] = child.cf_crashdump_location
            pair_list.append([bug_id, bug.dupe_of])
    # remove single bug_id
    ex_bugs = list(path_map.keys())
    # apply union_find
    uf = union_find.UnionFind(len(ex_bugs))
    for pair in pair_list:
        uf.unite(ex_bugs.index(pair[0]), ex_bugs.index(pair[1]))
    uf.id = [uf.find(i) for i in uf.id]
    # convert bug_id to dump
    for bug_id in ex_bugs:
        ex_dumps.append(path_map[bug_id])
    dump_dict = dict(zip(ex_dumps, uf.id))
    # extract dump path
    for group_id in set(uf.id):
        res = []
        for k, v in dump_dict.items():
            if v == group_id:
                if "\r\n" in k:
                    for path in k.split("\r\n"):
                        if "\\" in path:
                            path.replace("\\", "/")
                        if path.endswith(".trc") and path.startswith("/area51"):
                            res.append(path)
                else:
                    if "\\" in k:
                        k.replace("\\", "/")
                    if k.endswith(".trc") and k.startswith("/area51"):
                        res.append(k)
        # filter single group
        if len(res) > 1:
            result.append(res)
    print(result)


if __name__ == "__main__":
    dup_bug_lists_path = os.path.join(os.getcwd(), "json", "dup_bug_lists.json")
    try:
        with open(dup_bug_lists_path, "r") as f:
            dup_bug_lists = json.load(f)
    except FileNotFoundError:
        print("Can't find dup_bug_lists, please check!")
    group_dumps(dup_bug_lists)
