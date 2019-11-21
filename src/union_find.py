#!/usr/bin/env python
# -*- coding: utf-8 -*-


class UnionFind(object):
    id = []
    sz = []
    count = 0

    def __init__(self, n):
        i = 0
        self.count = n
        while i < n:
            self.id.append(i)
            self.sz.append(1)
            i += 1

    def find(self, x):
        while x != self.id[x]:
            x = self.id[x]
        return x

    def unite(self, x, y):
        idx = self.find(x)
        idy = self.find(y)
        if not self.find(x) == self.find(y):
            if self.sz[idx] < self.sz[idy]:
                self.id[idx] = idy
                self.sz[idy] += self.sz[idx]
            else:
                self.id[idy] = idx
                self.sz[idx] += self.sz[idy]
            self.count -= 1
