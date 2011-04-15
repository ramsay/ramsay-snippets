#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "breathalyzer.h"

#define MAX_BUFFER 1000
#define MAX_WORD_SIZE 20
typedef struct link word;

int main(int argc, char **argv)
{
    FILE *dictionary = fopen("twl06.txt", "r");
    FILE *wallpost = fopen(argv[1], "r");
    if (dictionary == NULL || wallpost == NULL) {
        printf("Need input and facebook word list.\n");
        return 1;
    }
    int i, d, words = 0;
    word *sentence, *pCur;
    char buffer1[MAX_BUFFER];
    char buffer2[MAX_BUFFER];
    sentence = (word *)malloc(sizeof(word));
    pCur = sentence;
    fgets(buffer1, MAX_BUFFER, wallpost);
    char *c = buffer1;
    while (*c != '\0' && *c !='\n') {
        if (*c >= 'a' && *c <= 'z') {
            *c += 'A' - 'a';
        }
        c++;
    }
    pCur->str = strtok(buffer1, " \r\n\t");
    while (pCur->str) {
        words++;
        pCur->next = (word *)malloc(sizeof(word));
        pCur = pCur->next;
        pCur->str = strtok(NULL, " \r\n\t");
    }
    int *distances = (int *)malloc(sizeof(int)*words);
    i = 0;
    for (pCur = sentence; pCur->next != NULL; pCur = pCur->next) {
        distances[i++] = strlen(pCur->str);
    }
    char * test;
    while(fgets(buffer2, MAX_BUFFER, dictionary)) {
        i = 0;
        test = strtok(buffer2, " \r\n");
        for (pCur = sentence; pCur->next != NULL; pCur = pCur->next) {
            d = levenshtein(test, pCur->str, distances[i]);
            if (d < distances[i]) {
                distances[i] = d;
            }
            i++;
        }
    }

    int sum = 0;
    for (i = 0; i < words; i++) {
        sum += distances[i];
    }
    printf("%d\n", sum);
    fclose(dictionary);
    fclose(wallpost);
    return 0;
}
