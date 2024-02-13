import sys


def trace_calls(frame, event, arg):
    co = frame.f_code
    func_name = co.co_name
    line_no = frame.f_lineno
    filename = co.co_filename
    if filename.endswith("py"):
        print(f"Call to {func_name} on line {line_no} of {filename}")
    return trace_calls


def test_func():
    import numpy as np

    a = np.array([1, 2, 3])
    print(a)

    b = np.array([4, 5, 6])
    print(b)


sys.settrace(trace_calls)
test_func()
sys.settrace(None)
