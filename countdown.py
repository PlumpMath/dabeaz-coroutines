# -*- coding: utf-8 -*-
#
# countdown.py
#
# A simple generator function

def countdown(n):
    print("Counting down from", n)
    while n > 0:
        yield n
        n -= 1
    print("Done counting down")


# Example use
if __name__ == '__main__':
    for i in countdown(10):
        print(i)

    c = countdown(5)
    print(c)

    # print(c.next())  # 3.5에서 동작하지 않음
    print(c.__next__())
    print(next(c))
