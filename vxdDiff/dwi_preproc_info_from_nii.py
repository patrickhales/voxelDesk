"""
Function to retrieve relevant information about the DWI data from the NIFTI file, and any existing json / bvals / bvecs
files with the same filename
"""

import ntpath
import os
import json

class dwi_preproc_info_from_nii:

    def __init__(self, niiFile=None):
        # check for json / bvals / bvecs files with the same name
        niiFolder, niiFileName = ntpath.split(niiFile)
        niiFileName_noext = niiFileName[:niiFileName.index('.nii')]

        jsonFile_test = os.path.join(niiFolder, niiFileName_noext + '.json')
        if os.path.exists(jsonFile_test):
            self.jsonFile = jsonFile_test
            print('- Found JSON file: %s' % self.jsonFile)
        else:
            self.jsonFile = None
            print('- No JSON sidecar found')

        bvecFile_test = os.path.join(niiFolder, niiFileName_noext + '.bvec')
        if os.path.exists(bvecFile_test):
            self.bvecFile = bvecFile_test
            print('- Found bvec file: %s' % self.bvecFile)
        else:
            self.bvecFile = None
            print('- No bvec file found')

        bvalFile_test = os.path.join(niiFolder, niiFileName_noext + '.bval')
        if os.path.exists(bvalFile_test):
            self.bvalFile = bvalFile_test
            print('- Found bval file: %s' % self.bvalFile)
        else:
            self.bvalFile = None
            print('- No bval file found')

        self.totalReadoutTime = None
        self.phaseEncodingDirection = None

        # if we've found a JSON file, read in the useful parameters for dwifslpreproc
        if self.jsonFile is not None:
            with open(self.jsonFile, 'r') as infile:
                jsonDat = json.load(infile)
                if 'TotalReadoutTime' in jsonDat:
                    self.totalReadoutTime = jsonDat['TotalReadoutTime']
                if 'PhaseEncodingDirection' in jsonDat:
                    self.phaseEncodingDirection = jsonDat['PhaseEncodingDirection']
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




