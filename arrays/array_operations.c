#include <stdio.h>

struct array
{
    int A[10];
    int size;
    int length;
};


// function declarations
void display(struct array arr);
void append(struct array *arr, int x);
void insert(struct array *arr, int index, int x);
int delete(struct array *arr, int index);
void swap(int *x, int *y);
int linear_search(struct array arr, int key);
int transposition_linear_search(struct array *arr, int key);
int move_to_head__linear_search(struct array *arr, int key);
int binary_search(struct array arr, int key);


// Main method
void main()
{
    struct array arr  = {{1, 3, 5, 6, 7}, 10, 5};
    display(arr);
    append(&arr, 9);
    display(arr);
    insert(&arr, 3, 22);
    display(arr);
    int a = delete(&arr, 3);
    display(arr);
    printf("\nThe deleted item is %d", a);
    printf("\n\n");
    struct array arr1  = {{1, 3, 5, 6, 7, 9, 2, 4}, 10, 8};
    struct array arr2  = {{1, 3, 5, 6, 7, 9, 2, 4}, 10, 8};
    struct array arr3  = {{1, 3, 5, 6, 7, 9, 2, 4}, 10, 8};
    struct array arr4  = {{1, 3, 5, 6, 7, 9, 11, 14, 17}, 10, 9};
    display(arr1);
    printf("\n\nLinear search 1");
    int key = 7;
    printf("\n%d is at index %d", key, linear_search(arr1, key));
    display(arr1);
    printf("\n");
    printf("\nLinear search 2");
    printf("\n%d is at index %d", key, transposition_linear_search(&arr2, key));
    display(arr2);
    printf("\n\nLinear search 3");
    printf("\n%d is at index %d", key, move_to_head__linear_search(&arr3, key));
    display(arr3);
    printf("\n\nBinary search");
    display(arr4);
    printf("\n%d is at index %d", key, binary_search(arr4, key));
}


// To display the array
void display(struct array arr)
{
    printf("\nElements are\n");
    for(int i = 0; i < arr.length; i++)
    {
        printf("%d  ", arr.A[i]);
    }
}

// To insert at the end of an array
void append(struct array *arr, int x)
{
    if(arr->length < arr->size)
    {
        arr->A[arr->length] = x;
        arr->length++;
    }
}

// To insert at any place of an array by giving index
void insert(struct array *arr, int index, int x)
{
    if(index >= 0 && index <= arr->length)
    {
        for(int i = arr->length; i > index; i--)
        {
            arr->A[i] = arr->A[i - 1];
        }
        arr->A[index] = x;
        arr->length++;
    }
}

// To delete an item from array and the value of that index
int delete(struct array *arr, int index)
{
    if(index >= 0 && index < arr->length)
    {
        int x = arr->A[index];
        for(int i = index; i < arr->length-1; i++)
        {
            arr->A[i] = arr->A[i + 1];
        }
        arr->length--;
        return x;
    }
    return 0;
}

// swapping of two elements
void swap(int *x, int *y)
{
    int temp;
    temp = *x;
    *x = *y;
    *y = temp;
}

// Normal linear search
int linear_search(struct array arr, int key)
{
    for(int i = 0; i < arr.length; i++)
    {
        if(key == arr.A[i])
        {
            return i;
        }
    }
    return -1;

}

// improved linear search by transposition method
int transposition_linear_search(struct array *arr, int key)
{
    for(int i = 0; i < arr->length; i++)
    {
        if(key == arr->A[i])
        {
            swap(&arr->A[i], &arr->A[i - 1]);
            return i;
        }
    }
    return -1;

}

// improved linear search by move to first/head method
int move_to_head__linear_search(struct array *arr, int key)
{
    for(int i = 0; i < arr->length; i++)
    {
        if(key == arr->A[i])
        {
            swap(&arr->A[i], &arr->A[0]);
            return i;
        }
    }
    return -1;

}

// Binary search
int binary_search(struct array arr, int key)
{

}