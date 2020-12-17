class DP(object):
    @staticmethod
    def lcs_position(seq_x, seq_y):
        pos_x = []
        pos_y = []
        m = len(seq_x)
        n = len(seq_y)
        # initialize dp matrix with 0
        dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]
        # fill dp matrix
        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0 or j == 0:
                    dp[i][j] = 0
                elif seq_x[i-1] == seq_y[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        # obtain positions of longest common subsequence
        i, j = m, n
        while i > 0 and j > 0:
            if seq_x[i-1] == seq_y[j-1]:
                pos_x.append(m - i)
                pos_y.append(n - j)
                i -= 1
                j -= 1
            elif dp[i-1][j] > dp[i][j-1]:
                i -= 1
            else:
                j -= 1
        return pos_x, pos_y

    @staticmethod
    def normalized_dist(seq_x, seq_y):
        m = len(seq_x)
        n = len(seq_y)
        # initialize dp matrix
        dp = [[i + j for j in range(n + 1)] for i in range(m + 1)]
        # fill dp matrix
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq_x[i-1] == seq_y[j-1]:
                    dist = 0
                else:
                    dist = 1
                dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + dist)
        return dp[m][n] / max(m, n)


class UnionFind(object):
    count = 0
    id, sz = [], []

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
        id_x = self.find(x)
        id_y = self.find(y)
        if not self.find(x) == self.find(y):
            if self.sz[id_x] < self.sz[id_y]:
                self.id[id_x] = id_y
                self.sz[id_y] += self.sz[id_x]
            else:
                self.id[id_y] = id_x
                self.sz[id_x] += self.sz[id_y]
            self.count -= 1
