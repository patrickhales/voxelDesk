# class to turn dicts into classes, for easier searching / auto-complete

from vxdTools.safeName import safeName

class dict_to_class:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            k = safeName(k)
            setattr(self, k, v)