# grepclose.py
#
# A coroutine that catches the close() operation

from coroutine import coroutine

@coroutine
def grep(pattern):
    print("Looking for %s" % pattern)
    try:
        while True:
            line = (yield)
            if pattern in line:
                print(line)
    except GeneratorExit:
        print("Going away. Goodbye")

@coroutine
def grep2(pattern):
    print("Looking for %s" % pattern)
    try:
        while True:
            line = (yield)
            if pattern in line:
                print(line)
    except GeneratorExit:
        yield "???"

@coroutine
def grep3(pattern):
    print("Looking for %s" % pattern)
    try:
        while True:
            line = (yield)
            if pattern in line:
                print(line)
    finally:
        print("clean up!")

# Example use
if __name__ == '__main__':
    g = grep("python")
    g.send("Yeah, but no, but yeah, but no\n")
    g.send("A series of tubes\n")
    g.send("python generators rock!\n")
    g.close()

    g = grep2("python")
    g.send("python generators rock!\n")
    g.close()

    g = grep3("python")
    g.send("python generators rock!\n")
    g.close()

