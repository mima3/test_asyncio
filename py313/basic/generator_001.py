import dis


def dump_gen(g):
    print(g, g.__dir__())
    print(g.gi_yieldfrom)
    print(g.gi_running)
    print(g.gi_frame)
    print(g.gi_suspended)
    print(g.gi_code)


def fib():
    a, b = 0, 1
    while 1:
        yield b
        a, b = b, a + b


g_fib = fib()
dis.dis(g_fib)  # type: ignore

print(next(g_fib))
print(next(g_fib))
print(next(g_fib))
print(next(g_fib))


class WriteLog(Exception):
    pass


def fib_with_except():
    a, b = 0, 1
    try:
        while 1:
            yield b
            a, b = b, a + b
    except WriteLog as log:
        print(log)
        return "LOG"
    else:
        return "OK"


g_fib = fib_with_except()
dis.dis(g_fib)  # type: ignore
print(g_fib.gi_suspended)  # type: ignore
print(next(g_fib))
print(g_fib.gi_suspended)  # type: ignore
print(next(g_fib))
print(next(g_fib))
print(next(g_fib))
try:
    g_fib.throw(WriteLog("hoge"))
except StopIteration as e:
    print(e)
    print(g_fib.gi_suspended)  # type: ignore
