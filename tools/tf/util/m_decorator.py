import functools
import tensorflow.compat.v1 as tf
from tools.basic.m_decorator import decorator_wrapper

templates = {}


@decorator_wrapper
def template_wrapper(func, name=""):
    name = name or func.__name__

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if templates.get(name, None):
            template = templates.get(name)
        else:
            template = tf.make_template(name, func, create_scope_now_=True)
            templates[name] = template
        return template(*args, **kwargs)

    return wrapper
