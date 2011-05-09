/**
 * Robert Ramsay
 * Test cases for the breathalyzer functions in C.
 */
#include "breathalyzer.h"
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv)
{
    printf("minimum(1, 2, 3) = %d\n", minimum(1, 2, 3));
    printf("distance(\"a\", \"a\") = %d\n", levenshtein("a", "a", 0));
    printf("distance(\"aa\", \"a\") = %d\n", levenshtein("aa", "a", 1));
    return 0;
}
