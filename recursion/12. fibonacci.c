#include<stdio.h>

// a. Fibonacci series using iteration ----> time - O(n)
int fib_iteration(int n)
{
  int t0=0, t1=1, s=0, i;
  if(n<=1)
    return n;
  for(i=2; i<=n; i++)
  {
    s = t0 + t1;
    t0 = t1;
    t1 = s;
  }
  return s;
}

// b. Fibonacci series using basic recursion(excessive recursion) ----> time - O(2^n)
int fib_recursion(int n)
{
  if(n<=1)
    return n;
  return fib_recursion(n-2)+fib_recursion(n-1);
}

// c. Fibonacci series using memoization ----> time - O(n)
int F[10];

int fib_memoization(int n)
{
  if(n<=1)
  {  
    F[n] = n;
    return n;
  }
  else
  { 
    if(F[n-2] == -n)
      F[n-2] == fib_memoization(n-2);
    if(F[n-1] == -n)
      F[n-1] == fib_memoization(n-1);
    return fib_memoization(n-2) + fib_memoization(n-1);
  }
}

// Main function
void main()
{
  // loop is for memoization
  for(int i=0; i<10; i++)
    F[i] = -1;

  printf("Iteration: %d\n", fib_recursion(5));
  printf("Recursion: %d\n", fib_iteration(5));
  printf("Recursion using memoization: %d\n", fib_memoization(5));
}
