# Part1 Introduction to Generators and Coroutines

## Generators

* generator: 단일 값이 아닌 일련의 값을 반환하는 함수
```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1
```
```
>>> for i in countdown(5): 
... print i,
...
54321
>>>
```
* 단일값이 아니라 `yield` 문을 이용하여 일련의 값을 'generate'함
* `for-loop`에서 사용 가능

* 일반적인 함수와는 동작이 다름
* generator를 호출하는 것은 generator 객체를 생성하는 것으로, 값 생산을 시작하지 않음

```python
def countdown(n):
    print("Counting down from", n)
    while n > 0:
        yield n
        n -= 1
```
```
>>> x = countdown(10)
>>> x
<generator object at 0x58490> >>>
```

## Generator Functions

* `next()`를 호출할 때 실행됨
```
>>> x = countdown(10)
>>> x
<generator object countdown at 0x100687990>
>>> next(x)
Counting down from 10
10 
>>>
```
    * Python3부터 `x.next()`는 사용할 수 없음. 대신 `x.__next__()`는 가능
        * https://www.python.org/dev/peps/pep-3114/
> This PEP proposes that the next method be renamed to `__next__` , consistent with all the other protocols in Python in which a method is implicitly called as part of a language-level protocol, and that a built-in function named next be introduced to invoke `__next__` method, consistent with the manner in which other protocols are explicitly invoked.
* `yield`로 값을 생산하고 실행을 멈춤
* `next()`를 호출해서 재개
```
>>> x.next()
9
>>> x.next()
8
>>>
```
* generator가 리턴하면 iteration을 멈춤
```
>>> x.next()
1
>>> x.next()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
>>>
```

## A Practical Example

* 'tail -f'를 python으로 구현해보기
```python
def follow(thefile):
    thefile.seek(0,2)      # Go to the end of the file
    while True:
         line = thefile.readline()
         if not line:
             time.sleep(0.1)    # Sleep briefly
             continue
         yield line
```
    * 웹 서버 로그 감시하기
```python
logfile = open("access-log")
for line in follow(logfile):
    print(line)
```

## Generators as Pipelines

* 파이프라인 처리는 generator의 강력한 응용 예
* unix의 쉘 파이프와 비슷
```
input sequence --> generator --> generator --> for x in s:
```
* Idea: generator를 파이프에 넣은 다음, `for-loop`를 통해 값을 가져올 수 있음

## A Pipeline Example

* 'python' 낱말이 있는 모든 로그를 출력하기
```python
def grep(pattern,lines):
    for line in lines:
        if pattern in line:
             yield line

# Set up a processing pipe : tail -f | grep python
logfile  = open("access-log")
loglines = follow(logfile)
pylines  = grep("python",loglines)

# Pull results out of the processing pipeline
for line in pylines:
    print(line,)
```

## Yield as an Expression

* Python2.5부터 `yield`를 expression으로 사용 가능
* PEP-342: https://www.python.org/dev/peps/pep-0342/
    * https://docs.python.org/2.5/whatsnew/pep-342.html
        * Python2.3에서 generator가 처음 등장했으나 값을 생산하는 것만 가능
            * 값을 전달하기 위한 편법으로 전역변수를 이용하기도 
        * 2.5에서 외부에서 generator로 값을 전달하는 방법을 제공: generator를 단방향 값 생성자에서 양방향 생성자/소바지로 바꿈
            * 외부에서 `send(value)`로 전달. `next()`는 `send(None)`과 동일
            * statement에서 expression으로 바뀜
            * 값을 전달할 때 다른 표현식과 섞어 쓸 경우 반드시 `yield` 표현식은 괄호로 묶어야 함
```python
val = (yield i) + 12   # O
val = yield i + 12     # X
val = (yield i)        # O
val = yield i          # O
```
        * 예, 실행 중간에 값을 못 바꾸는 카운터
```python
def counter (maximum):
    i = 0
    while i < maximum:
        yield i
        i += 1
```
        * 예, `send()`를 이용하여 실행 중간에 값을 바꾸는 예
```python
def counter (maximum):
    i = 0
    while i < maximum:
        val = (yield i)
        # If value provided, change counter
        if val is not None:
            i = val
        else:
            i += 1
```
```
>>> it = counter(10)
>>> print it.next()
0
>>> print it.next()
1
>>> print it.send(8)
8
>>> print it.next()
9
>>> print it.next()
Traceback (most recent call last):
  File ``t.py'', line 15, in ?
    print it.next()
StopIteration
```
        * 추가로 제공하는 메소드
            * `throw(type, value=None, trackback=None)`
                * generator 내부에서 예외를 일으키기 위한 용도
            * `close()`
                * `GeneratorExit` 예외를 발생시킴
                * generator 내에서 새 `GeneratorExit` 예외를 발생시켜 반복을 종료
                * 이 예외가 발생하면 generator의 코드는 `GeneratorExit` 또는 `StopIteration`을 발생시켜야함
                * `GeneratorExit` 예외를 포착하고 값을 반환하는 것은 옳지 않으며 `RuntimeError`를 트리거함
                * 함수가 다른 예외를 발생시키는 경우 해당 예외는 호출자에게 전달됨
                * `close()`는 generator가 가비지 수집될 때 파이썬의 가비지 수집기에 의해 호출됨
* 할당문의 오른쪽에 사용할 수 있음
```python
def grep(pattern):
    print("Looking for %s" % pattern)
    while True:
        line = (yield)
        if pattern in line:
            print(line,)
```
* Question: 이것은 가치는?


## Coroutine Execution

* generator와 똑같은 실행
* coroutine을 실행했을 때 아무 일도 발생하지 않음
* `next()`, `send()`에 반응
```
>>> g = grep("python")  # 아무런 출력이 없음
>>> g.next()            # 실행  
Looking for python
>>>
```

## Coroutines

* 보다 일반적으로 `yield`를 사용하면 `coroutine`을 얻습니다.
* 값을 생성하는 것 이상을 할 수 있음
* 전달 받은 값을 소비할 수 있음
```python
g = grep("python")
g.send(None) # Prime it
g.send("Yeah, but no, but yeah, but no")
g.send("A series of tubes")
g.send("python generators rock!")
```
* `yield`로 값을 받음


## Coroutine Priming

* 모든 coroutine은 먼저 `next()`나 `.send(None)`을 이용해 준비하는 과정이 필요
* 첫 번째 `yield` 표현식의 위치로 실행 위치를 이동시킴
```python
def grep(pattern):
    print("Looking for %s" % pattern)
    while True:
        line = (yield)  # <--- 첫 next() 호출 때, 여기로 이동! line에 값을 전달하기 직전
        if pattern in line:
            print(line,)
```
* 값을 받을 준비가 되었음

## Using a Decorator

* `next()`를 호출하는 것은 잊기 쉬움
* coroutine을 decorator로 감싸서 해결
```python
def coroutine(func):
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        next(cr)
        return cr
    return start

@coroutine
def grep(pattern):
```

## Catching `close()`

* `close()` 호출을 잡을 수 있음
```python
@coroutine
def grep(pattern):
    print("Looking for %s" % pattern)
    try:
        while True:
            line = (yield)
            if pattern in line:
                print(line,)
    except GeneratorExit:
        print("Going away. Goodbye")

g = grep("python")
g.send("Yeah, but no, but yeah, but no\n")
g.send("A series of tubes\n")
g.send("python generators rock!\n")
g.close()
```
* 예외를 무시할 수 없고 정리해서 반환하는 것이 유일한 합법적인 조치임
* `close()`를 호출했을 때, 예외를 잡아 값을 반환하는 것은 비합법적인 조치
```python
@coroutine
def grep2(pattern):
    print("Looking for %s" % pattern)
    try:
        while True:
            line = (yield)
            if pattern in line:
                print(line)
    except GeneratorExit:
        yield '???'

g = grep2("python")
g.send("Yeah, but no, but yeah, but no\n")
g.send("A series of tubes\n")
g.send("python generators rock!\n")
g.close()
```
```
Looking for python
python generators rock!

Traceback (most recent call last):
  File "/Users/cybaek/PycharmProjects/dabeaz-coroutines/grepclose.py", line 24, in <module>
    g.close()
RuntimeError: generator ignored GeneratorExit
```
* `GeneratorExit`를 잡아 리소스 정리하는 경우에는 `GeneratorExit`예외를 잡아 처리하는 것보다 `try...finally` 구문을 추천
```python
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

g = grep3("python")
g.send("python generators rock!\n")
g.close()
```

## Throwing an Exception

* coroutine 내부에 예외를 던질 수 있음
```
>>> g = grep("python")
>>> next(g) # Prime it
Looking for python
>>> g.send("python generators rock!")
python generators rock!
>>> g.throw(RuntimeError, "You're hosed")
Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "<stdin>", line 4, in grep
RuntimeError: You're hosed
>>>
```
* 예외는 yield 식에서 발생
* 일반적인 방법으로 핸들링할 수 있음


## Interlude

* 비슷해보이지만 generator와 coroutine은 기본적으로 다른 컨셉
* generator는 값을 생산하지만
* coroutine은 값을 소비함
* It is easy to get sidetracked because methods meant for coroutines are sometimes described as a way to tweak generators that are in the process of producing an iteration pattern (i.e., resetting its value). This is mostly bogus.

## A Bogus Example

* 값을 생성하고 받는 "generator"
```python
def countdown(n):
    print("Counting down from", n)
    while n >= 0:
        newvalue = (yield n)
        # If a new value got sent in, reset n with it
        if newvalue is not None:
            n = newvalue
        else:
            n -= 1
```
* It runs, but it's "flaky" and hard to understand
```python
c = countdown(5)
    for n in c:
        print(n)
        if n == 5:
            c.send(3)
```
    * Notice how a value got "lost" in the iteration protocol
```
5
2
1
0
```

## Keeping it Straight

* generator는 순회를 위해 값을 생성
* coroutine은 데이터 소비자
* To keep your brain from exploding, you don't mix the two concepts together
* coroutine은 순회/반복과 상관이 없음!
* Note: coroutine에서 값을 생성할 수 있으나, 순회와는 상관이 없음

