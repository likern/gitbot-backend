from pydantic import BaseModel


def mongodb(func):
    def wrapper(*args, **kwargs):
        def convert(obj):
            if isinstance(obj, BaseModel):
                return obj.dict(skip_defaults=True)
            return obj

        if not (len(args) or len(kwargs)):
            return

        new_args = (*map(convert, args),)
        new_kwargs = (*map(convert, kwargs),)
        func(*new_args, **new_kwargs)
    return wrapper
