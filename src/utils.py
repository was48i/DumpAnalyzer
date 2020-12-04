class Utils(object):
    """
    Several algorithms used by our approach.
    """
    @staticmethod
    def lcs_index(seq_x, seq_y):
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
        # obtain the index of longest common subsequence
        index_x = []
        index_y = []
        i, j = m, n
        while i > 0 and j > 0:
            if seq_x[i-1] == seq_y[j-1]:
                index_x.append(i-1)
                index_y.append(j-1)
                i -= 1
                j -= 1
            elif dp[i-1][j] > dp[i][j-1]:
                i -= 1
            else:
                j -= 1
        return index_x, index_y

    @staticmethod
    def normalized_dist(str_x, str_y):
        m = len(str_x)
        n = len(str_y)
        # initialize dp matrix
        dp = [[i + j for j in range(n + 1)] for i in range(m + 1)]
        # fill dp matrix
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str_x[i-1] == str_y[i-1]:
                    dist = 0
                else:
                    dist = 1
                dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + dist)
        return dp[m][n] / max(m, n)
