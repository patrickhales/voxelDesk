# function to read the Siemens CSA header info from a DICOM file, and write this to an easy to read text file if requested
# returns a dict called 'csa'

import pydicom
import ntpath
import os

def read_siemens_csa(dcmFile=None, writeTextFile=False):

    txtFileName = 'csa.txt'
    csa = None

    dcmFolder, dcmFileName = ntpath.split(dcmFile)
    txtFile = os.path.join(dcmFolder, txtFileName)

    # read the dcmFile
    ds = pydicom.read_file(dcmFile)

    # try to parse the Siemens CSA header info. These are stored in Image Header Info (0029,1020), or on the Vida, (0021, 1019).
    # These use a series of tags and null terminated strings.
    # the trick to reading these is to only look at the ASCII text in between the flags
    # ### ASCCONV BEGIN and ### ASCCONV END
    targetDicomTag = None
    if 'SoftwareVersions' in ds:
        if ds.SoftwareVersions == 'syngo MR XA11' or ds.SoftwareVersions == 'syngo MR XA20':
            targetDicomTag = 0x00211019
        if ds.SoftwareVersions == 'syngo MR D13D' or ds.SoftwareVersions == 'syngo MR E11':
            targetDicomTag = 0x00291020

    # check for Siemens enhanced DICOMS
    enh_check1 = False
    enhtag1 = 0x52009229
    enhtag2 = 0x002110fe
    enhtag3 = 0x00211019
    enhanced_flag = False
    if 0x52009229 in ds:
        if enhtag2 in ds[enhtag1][0]:
            if enhtag3 in ds[enhtag1][0][enhtag2][0]:
                enhanced_flag = True


    if targetDicomTag is not None:
        csa1 = None

        if targetDicomTag in ds:
            csa1 = str(ds[targetDicomTag].value)
        else:
            if enhanced_flag:
                csa1 = str(ds[enhtag1][0][enhtag2][0][enhtag3].value)

        if csa1 is not None:

            if 'ASCCONV BEGIN' in csa1 and 'ASCCONV END' in csa1:

                csa1text = csa1[csa1.index('ASCCONV BEGIN'):csa1.index('ASCCONV END')]
                parts = csa1text.split('\\n')

                # each item in the parts list will look like:
                # <parameter name>\\t = \\t""<parameter value>""
                csa = {}
                for txt in parts:
                    if '\\t' in txt:
                        pname_endInd = txt.index('\\t = ')
                        pname = txt[0:pname_endInd]
                        value_startInd = pname_endInd + 7
                        value = txt[value_startInd:]
                        csa[pname] = value

            if writeTextFile:
                # convert the csa dictionary to a list of strings
                list_of_strings = [f'{key} : {csa[key]}' for key in csa]
                # write the text file
                print('Writing: %s' % txtFile)
                with open(txtFile, 'w') as my_file:
                    [my_file.write(f'{st}\n') for st in list_of_strings]

    return csa

