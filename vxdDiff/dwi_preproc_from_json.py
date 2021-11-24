"""
Class to read useful info from a json file, for use in dwifslpreproc
"""

import json
import numpy as np

class dwi_preproc_from_json:
    def __init__(self, jsonFile=None):

        self.PhaseEncodingDirection = None
        self.TotalReadoutTime = None

        if jsonFile is not None:
            with open(jsonFile, 'r') as infile:
                jsonDat = json.load(infile)

            if 'PhaseEncodingDirection' in jsonDat:
                self.PhaseEncodingDirection = jsonDat['PhaseEncodingDirection']
            if 'TotalReadoutTime' in jsonDat:
                self.TotalReadoutTime = jsonDat['TotalReadoutTime']
            if 'dw_scheme' in jsonDat:
                self.dwischeme = jsonDat['dw_scheme']
                # collate the bvalues to determine the number of shells
                self.bvalues = []
                for thisgrad in self.dwischeme:
                    self.bvalues.append(thisgrad[3])
                shell_bvals, counts = np.unique(self.bvalues, return_counts=True)
                # apply some rounding to equalize very similiar bvals
                self.shell_bvals = [round(n, -1) for n in shell_bvals]
                self.shells = len(self.shell_bvals)
                self.shell_vols = counts

            if 'size' in jsonDat:
                self.size = jsonDat['size']


