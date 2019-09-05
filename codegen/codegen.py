import inspect


def get_generated_code(fn):
    return inspect.getsource(fn)
