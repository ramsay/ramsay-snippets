/**
 * Robert Ramsay 2011 breathalyzer functions.
 */
#include <stdlib.h>
#include <string.h>

int minimum(int i, int j, int k)
{
    if (i < j && i < k) {
        return i;
    } else if (j < k) {
        return j;
    }
    return k;
}

int levenshtein(const char *str1, const char *str2, int threshold)
{
    /**
     * d = [[i if j==0 else j if i==0 else 0
        for i in range(len(word1)+1)]
        for j in range(len(word2)+1)]
    for j in range(1, len(word1) + 1):
        for i in range(1, len(word2) + 1):
            if word1[j-1] == word2[i-1]:
                d[i][j] = d[i-1][j-1]
            else:
                d[i][j] = min([d[i-1][j], d[i][j-1], d[i-1][j-1]]) + 1
    return d[-1][-1]
    */
    int m = strlen(str1)+1;
    int n = strlen(str2)+1;
    int i, j;
    int d[m][n];
    for (i = 0; i < m; i++) {
        d[i][0] = i;
    }
    for (i = 0; i < n; i++) {
        d[0][i] = i;
    }

    for (j = 1; j < n; j++) {
        for (i = 1; i < m; i++) {
            if (str1[i-1] == str2[j-1]) {
                d[i][j] = d[i-1][j-1];
            } else {
                d[i][j] = minimum(
                    d[i-1][j],
                    d[i][j-1],
                    d[i-1][j-1]) + 1;
            }
        }
    }
    return d[m-1][n-1];
}

/**
 * Linked List element.
 */
struct link {
    char *str;
    struct link * next;
};
