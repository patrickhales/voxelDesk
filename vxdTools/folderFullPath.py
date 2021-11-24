"""
Function to ensure a folder paths are complete (for partial paths given from the command line)
"""

import os
# check if user has passed full path or relative path to the dicom folder

def folderFullPath(folderPath):

    if not os.path.isabs(folderPath):
        wdir = os.getcwd()
        folderPathFull = os.path.join(wdir, folderPath)
    else:
        folderPathFull = folderPath

    return folderPathFull


