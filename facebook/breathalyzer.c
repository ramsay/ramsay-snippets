#include <stdio.h>
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

int levenshtein(char *str1, char *str2, int threshold)
{
    int m = strlen(str1);
    int n = strlen(str2);
    int i, j;
    int d[m][n];
    for (i = 0; i < m; i++) {
        d[i][0] = i;
    }
    for (i = 0; i < n; i++) {
        d[0][i] = i;
    }

    for (i = 0; i < m; i++) {
        for (j = 0; i< n; i++) {
            if (str1[i] == str2[j]) {
                d[i][j] = d[i-1][j-1];
            } else {
                d[i][j] = minimum(d[i-1][j], d[i][j-1], d[i-1][j-1]);
            }
        }
    }
    return d[m][n];
}

#define MAX_BUFFER 255
#define MAX_WORDS 100
int main(int argc, char **argv)
{
    FILE *dictionary = fopen("twl06.txt", "r");
    FILE *wallpost = fopen(argv[1], "r");
    if (dictionary == NULL || wallpost == NULL) {
        printf("Need input and facebook word list.\n");
        return 1;
    }
    int i;
    int words = 0;
    char **sentence;
    char buffer[MAX_BUFFER];
    fgets(buffer, MAX_BUFFER, wallpost);
    sentence[words] = strtok(buffer, " \r\n\t");
    while (sentence[words++]) {
        sentence[words] = strtok(NULL, " \r\n\t");
    }

    int distances[words];
    for (i = 0; i < words; i++) {
        distances[i] = strlen(sentence[i]);
    }
    while(fgets(buffer, MAX_BUFFER, dictionary)) {
        for (i = 0; i < words; i++) {
            distances[i] = levenshtein(buffer, sentence[i], distances[i]);
        }
    }
    int sum = 0;
    for (i = 0; i < words; i++) {
        sum += distances[i];
    }
    printf("%d", sum);
    return 0;
}
