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


def addBackslashEscape(testString):
    """add an \ escape character before any whitespaces in a string"""
    underscores = r""" """
    safeName = ""
    for c in testString:
        if c in underscores:
            c = "\ "
        safeName += c
    return safeName


def spaceToUnderscore(testString):
    """add an underscore character in place of any whitespaces in a string"""
    underscores = r""" """
    safeName = ""
    for c in testString:
        if c in underscores:
            c = "_"
        safeName += c
    return safeName