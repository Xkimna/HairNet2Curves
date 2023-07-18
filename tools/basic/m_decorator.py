import inspect
import functools


def decorator_wrapper(func):
    """
    Allow to use decorator either with arguments or not
    """

    def is_func_arg(*args, **kwargs):
        return len(args) == 1 and len(kwargs) == 0 and (
                inspect.isfunction(args[0]) or isinstance(args[0], type))

    if isinstance(func, type):
        def class_wrapper(*args, **kwargs):
            if is_func_arg(*args, **kwargs):
                return func()(*args, **kwargs)  # create class before usage
            return func(*args, **kwargs)

        class_wrapper.__name__ = func.__name__
        class_wrapper.__module__ = func.__module__
        return class_wrapper

    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        if is_func_arg(*args, **kwargs):
            return func(*args, **kwargs)

        def functor(user_func):
            return func(user_func, *args, **kwargs)

        return functor

    return func_wrapper
