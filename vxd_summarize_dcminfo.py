#!/usr/bin/env python

# function to summarize dicom header info and write out to a text file

import argparse
import os
import sys
from vxdDicom.collate_dicom_info import collate_dicom_info


if __name__ == '__main__':

    # Construct the argument parser
    ap = argparse.ArgumentParser(add_help=False)

    # Add the arguments to the parser
    required = ap.add_argument_group('required arguments')
    optional = ap.add_argument_group('optional arguments')
    required.add_argument("-i", "--input", required=True, help="Input DICOM file")
    optional.add_argument('-f', '--full', action='store_true', help='Write full set of DICOM tags (as well as key tags)')
    optional.add_argument('-h', '--help', action='help', help='Show this help message and exit')
    args = ap.parse_args()

    #  --- Source DICOM file
    dcmFile = args.input
    # check if user has passed full path or relative path to the input file
    if not os.path.isabs(dcmFile):
        wdir = os.getcwd()
        dcmFileFullPath = os.path.join(wdir, dcmFile)
        dcmFile = dcmFileFullPath
    if not os.path.exists(dcmFile):
        print('Error: Input file cannot be found: %s' % dcmFile)
        print('Check filename/path')
        sys.exit(1)
    else:
        print('')
        print('- Source DICOM File = %s' % (dcmFile))

    if args.full:
        fullOutput = True
    else:
        fullOutput = False

    # read in the standard DICOM tags, and the Siemens CSA header if it exists
    ds_csa, ds_csa_key = collate_dicom_info(dcmFile)

    # output the results as text files
    seriesFolder, filename = os.path.split(dcmFile)
    filename_parts = os.path.splitext(filename)
    filename_noext = filename_parts[0]
    studyFolder, seriesFolderName = os.path.split(seriesFolder)
    outFile_full = os.path.join(studyFolder, seriesFolderName + '_dcminfo.txt')
    outFile_key = os.path.join(studyFolder, seriesFolderName + '_dcminfo_key.txt')
    if fullOutput:
        print(' ')
        print('Writing: %s' % outFile_full)
        fo = open(outFile_full, "w")
        for k, v in ds_csa.items():
            fo.write(str(k) + ': ' + str(v) + '\n')
        fo.close()
    print(' ')
    print('Writing: %s' % outFile_key)
    fo = open(outFile_key, "w")
    for k, v in ds_csa_key.items():
        fo.write(str(k) + ': ' + str(v) + '\n')
    fo.close()



