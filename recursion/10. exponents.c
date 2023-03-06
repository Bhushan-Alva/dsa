#include<stdio.h>

// a. Basic recursion ----> time - O(n), space - O(n)

int pow_basic(int m, int n)
{
  if(n > 0)
  {
    return pow_basic(m, n - 1) * m;
  }
  return 1;
}

// b. Faster recursion ----> time - O(logn), space - O(logn)

int pow_fast(int m, int n)
{
  if(n == 0)
    return 1;
  if (n % 2 == 0)
    return pow_fast(m * m, n / 2);
  else
    return m * pow_fast(m * m, (n - 1) / 2);
}
void main()
{
  printf("Basic Recursion: %d\n", pow_basic(3, 4));
  printf("Faster recursion: %d\n", pow_fast(3, 4));
}
