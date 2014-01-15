import new

def monkeypatch(cls):
    def decorator(orig):
        if isinstance(orig, (new.classobj, type)):
            cls2 = orig
            class Before(object): pass
            b = Before()
            setattr(cls, "Before" + cls2.__name__, b)
            setattr(cls2, "super", b)
            for k, v in cls2.__dict__.items():
                if isinstance(v, new.function):
                    f = decorator(v)
                    setattr(b, f.func_name, f.__original__)
                    v.__original__ = f.__original__
            return cls2
        else:
            f = orig
            func_name = f.func_name
            replacement_method = new.instancemethod(f, None, cls)
            def monkeypatch(*a, **k):
                return replacement_method(*a, **k)
            f = monkeypatch
            f.func_name = func_name
            method = getattr(cls, func_name, None)
            f.__original__ = method
            setattr(cls, func_name,
                    new.instancemethod(f, None, cls))
            return f
    return decorator
