#include<stdio.h>
int F[10];
int fib(int n)
{
  if(n<=1)
  {  
    F[n] = n;
    return n;
  }
  else
  { 
    if(F[n-2] == -n)
      F[n-2] == fib(n-2);
    if(F[n-1] == -n)
      F[n-1] == fib(n-1);
    return fib(n-2)+fib(n-1);
  }
}
void main()
{
  for(int i=0; i<10; i++)
    F[i] = -1;
  printf("%d", fib(5));
}