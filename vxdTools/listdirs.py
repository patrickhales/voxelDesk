import os

def listdirs(parentFolder):
    """function to list directories in a parent folder"""
    return [d for d in sorted(os.listdir(parentFolder)) if os.path.isdir(os.path.join(parentFolder, d))]