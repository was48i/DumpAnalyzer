class DP(object):
    """
    Several dynamic programming algorithms that will be used.
    """
    @staticmethod
    def lcs_position(seq_x, seq_y):
        """
        Obtain the position information of longest common subsequence via top first.
        Args:
            seq_x: A sequence to be iterated.
            seq_y: A sequence to be iterated.
        Returns:
            The position information of longest common subsequence.
        """
        pos_x, pos_y = [], []
        m, n = len(seq_x), len(seq_y)
        # initialize dp matrix with 0
        dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]
        # fill dp matrix
        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0 or j == 0:
                    dp[i][j] = 0
                elif seq_x[m-i] == seq_y[n-j]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        # obtain positions of longest common subsequence
        i, j = m, n
        while i > 0 and j > 0:
            if seq_x[m-i] == seq_y[n-j]:
                pos_x.append(m - i)
                pos_y.append(n - j)
                i -= 1
                j -= 1
            elif dp[i - 1][j] > dp[i][j - 1]:
                i -= 1
            else:
                j -= 1
        return pos_x, pos_y

    @staticmethod
    def normalized_dist(seq_x, seq_y):
        """
        Obtain the normalized distance between two sequences.
        Args:
            seq_x: A sequence to be iterated.
            seq_y: A sequence to be iterated.
        Returns:
            The normalized distance between two sequences.
        """
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


class UF:
    """
    An implementation of Union-Find algorithm.
    Attributes:
        id: The identifier of each tree.
        rank: The weight of each tree.
    """
    def __init__(self, n):
        self.id = list(range(n))
        self.rank = [0] * n

    def find(self, p):
        """
        Obtain the tree identifier for an element node via path compression.
        Args:
            p: An element node.
        Returns:
            The tree identifier.
        """
        while p != self.id[p]:
            p = self.id[p] = self.id[self.id[p]]
        return p

    def union(self, p, q):
        """
        Combine trees containing two element nodes into a single tree.
        Args:
            p: An element node.
            q: An element node.
        """
        i, j = self.find(p), self.find(q)
        if i == j:
            return
        if self.rank[i] < self.rank[j]:
            self.id[i] = j
        else:
            if self.rank[i] == self.rank[j]:
                self.rank[i] += 1
            self.id[j] = i
