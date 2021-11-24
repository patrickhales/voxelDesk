import pickle

def readLogFile(logFile):
    """quick function to save time when opening logFiles"""
    f = open(logFile, 'rb')
    sorter = pickle.load(f)
    f.close()
    return sorter