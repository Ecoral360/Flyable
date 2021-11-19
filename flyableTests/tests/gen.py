def fn():
    for i in range(10):
        if i % 3 == 2:
            yield "stop!"
        yield i


for i in (j for j in range(10000)):
    print(i)

