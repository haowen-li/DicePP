from inspect import signature
from functools import wraps

def TypeAssert(*type_args, **type_kwargs):
    # 一个装饰器, 用来检查参数类型
    # 用法: 
    # @TypeAssert(int, z=str)
    # def display(x, y, z):
    #     print(x, y, z)
    def decorate(func):
        sig = signature(func)
        bound_types = sig.bind_partial(*type_args, **type_kwargs).arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs)
            for name, value in bound_values.arguments.items():
                if name in bound_types:
                    if not isinstance(value, bound_types[name]):
                        raise TypeError('Argument {} must be {}'.format(name, bound_types[name]))
            return func(*args, **kwargs)
        return wrapper
    return decorate