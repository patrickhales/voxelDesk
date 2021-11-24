import os

def safeName(testString):
    """Remove any potentially dangerous or confusing characters from
    the testString by mapping them to reasonable subsitutes"""
    underscores = r"""+`~!@#$%^&*(){}[]/=\|<>,.":' """
    safeName = ""
    for c in testString:
        if c in underscores:
            c = "_"
        safeName += c
    return safeName
