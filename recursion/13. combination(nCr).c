#include <stdio.h>

// a. Combination using factorial ----> time - O(n)
// 1. create fact function
int fact(int n)
{
    if(n==0)
        return 1;
    return fact(n - 1) * n;
}

// 2. use fact function for nCr formula
int combination_fact(int n, int r)
{
    int t1, t2, t3;
    t1 = fact(n);
    t2 = fact(r);
    t3 = fact(n-r);
    return t1 / (t2  * t3);
}

// b. recursion using pascal's triangle ----> time - O(2^n) or  O(n^n)
int combination_pascal(int n, int r)
{
    if(r == 0 || n == r)
        return 1;
    else
        return combination_pascal(n-1, r-1) + combination_pascal(n-1, r);
}

// Main function
int main()
{
    printf("Using factorial: %d\n", combination_fact(7, 4));
    printf("Using pascal's triangle: %d\n", combination_pascal(7, 4));
    return 0;
}
