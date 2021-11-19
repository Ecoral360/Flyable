def fib(n):
    a = 0
    b = 1
    for i in range(n):
        y = b
        b = a + b
        a = y
    return a


result = fib(10)
print(result)
