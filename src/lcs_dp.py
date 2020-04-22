def lcs_dp(x, y):
    m = len(x)
    n = len(y)
    dp = [[0 for i in range(n + 1)] for i in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                dp[i][j] = 0
            elif x[i - 1] == y[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    # get LCS result
    index = dp[m][n]
    result = [""] * index
    x_pos = []
    y_pos = []
    i = m
    j = n
    while i > 0 and j > 0:
        if x[i - 1] == y[j - 1]:
            result[index - 1] = x[i - 1]
            x_pos.append(i - 1)
            y_pos.append(j - 1)
            i -= 1
            j -= 1
            index -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    x_pos.reverse()
    y_pos.reverse()
    return result, x_pos, y_pos


__all__ = [
    "lcs_dp"
]
