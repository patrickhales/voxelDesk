#!/usr/bin/env python

from vxdSort import dicomsort
import os
import sys
from nipype.interfaces.dcm2nii import Dcm2niix
import argparse
import pydicom
import subprocess
from vxdSort.dicomTree import dTree
from vxdSort.anonymize_dicom_root import anonymize
from vxdTools.safeName import safeName
from vxdTools.folderFullPath import folderFullPath
from vxdTools.readConfigFile import readConfigFile


if __name__ == '__main__':

    # Construct the argument parser
    ap = argparse.ArgumentParser(add_help=False)

    # Add the arguments to the parser

    required = ap.add_argument_group('required arguments')
    optional = ap.add_argument_group('optional arguments')

    required.add_argument("-i", "--input", required=True, help="Input DICOM directory")
    optional.add_argument("-a", "--anon", required=False, help="Create anonymized DICOMs", action='store_true')
    optional.add_argument("-c", "--codes", required=False, help="Patient codes for anonymization - use comma separated list in quotes")
    optional.add_argument("-n", "--nifti", required=False, help="Convert sorted DICOMs to NIFTI", action='store_true')
    optional.add_argument('-h', '--help', action='help', help='Show this help message and exit')

    args = ap.parse_args()

    # load the default parameters from the config file
    config = readConfigFile()

    # Define source dicom folder
    dicomFolder = args.input

    # check if user has passed full path or relative path to the source dicom folder
    dicomFolder = folderFullPath(dicomFolder)

    print('')
    print('-Source DICOM Folder = %s' % dicomFolder)

    # Define target dicom folder
    dicomOutputFolderBase = dicomFolder
    sortedDicomFolder = os.path.join(dicomOutputFolderBase, config['sortedDicomFolderName'])

    """
    # check if this folder already exists. If so, define a new target folder
    if os.path.exists(sortedDicomFolder):
        sortedDicomFolder = os.path.join(dicomOutputFolderBase, config['sortedDicomFolderName'] + '_new')
    """

    print('-Target DICOM Folder = %s' % sortedDicomFolder)

    if args.nifti:
        createNifti = True
    else:
        createNifti = False

    if args.anon:
        anonymizeRoot = True
    else:
        anonymizeRoot = False

    if args.codes:
        patientIDs_str = args.codes
        # remove whitespaces between commas
        patientIDs_str = patientIDs_str.replace(' ', '')
        patientIDs = list(patientIDs_str.split(','))
        # remove any characters from the list which would cause problems with folder names
        for pctr, patientID in enumerate(patientIDs):
            patientIDs[pctr] = safeName(patientID)
    else:
        patientIDs = None

    verbose = False

    print('')

    print('Sorting DICOM files in %s...' % dicomFolder)

    # define the target pattern for dicom file output
    targetPatternStr = config['defaultTargetPattern']
    targetPattern = sortedDicomFolder + targetPatternStr

    # create an instance of the DICOMSorter class
    sorter = dicomsort.DICOMSorter()
    # set the options for running the sorter
    options = {}
    options['sourceDir'] = dicomFolder
    options['targetPattern'] = targetPattern
    options['deleteSource'] = False
    options['verbose'] = verbose

    if not os.path.exists(options['sourceDir']):
        print("Source directory does not exist: %s" % options['sourceDir'])
        sys.exit(1)

    sorter.setOptions(options)

    # run the sorter
    sorter.renameFiles()

    print("...Renamed %d files, skipped the following %d file(s)" % (sorter.filesRenamed, sorter.filesSkipped))
    if len(sorter.skippedFiles) > 0:
        for skippedFile in sorter.skippedFiles:
            print('\t%s' % skippedFile)

    # Dicoms are now sorted

    # Create the dicom tree structure, based on the information in the sorter object
    print('')
    print('%s contains:' % (sortedDicomFolder))
    dt = dTree(sorter)
    dt.printTree()

    # If anonymization has been requested, run it now
    if anonymizeRoot:
        sortedDicomFolderAnon, patientLookup = anonymize(dicomFolder, sorter, patientIDs=patientIDs)
        # re-run the sorter in the anonymized dicom folder, to create a new logFile
        targetPatternStr = config['defaultTargetPattern']
        targetPatternAnon = sortedDicomFolderAnon + targetPatternStr
        sorterAnon = dicomsort.DICOMSorter()
        optionsAnon = {}
        optionsAnon['sourceDir'] = sortedDicomFolderAnon
        optionsAnon['targetPattern'] = targetPatternAnon
        optionsAnon['deleteSource'] = False
        optionsAnon['verbose'] = False
        optionsAnon['keepGoing'] = True
        sorterAnon.setOptions(optionsAnon)
        # run the sorter
        sorterAnon.renameFiles()
        print("...Renamed %d files, skipped the following %d file(s)" % (sorterAnon.filesRenamed, sorterAnon.filesSkipped))

    else:
        # if not anonymizing, create a patientLookup dict with equal key/value pairs
        patientLookup = {}
        for pctr, patientID in enumerate(dt.patients):
            patientLookup[patientID] = dt.patients[pctr]

    if createNifti:
        # prepare a mirrored folder structure for the niftis, and convert the dicoms
        # each dict key in renamedFiles is a new directory path created while sorting
        # values for the keys are lists of new dicom filenames within directory
        print('')
        print('Writing NIFTI files...')
        for folder in sorter.renamedFiles:
            # the mirrored nifti folder will match the dicom folder, but base folder name changes
            part1 = folder[:folder.index(config['sortedDicomFolderName'])]
            part2 = folder[folder.index(config['sortedDicomFolderName'])+len(config['sortedDicomFolderName']):]
            niiFolder = part1 + config['sortedNiftiFolderName'] + part2
            # also change the patient subFolder name, so that patient names are not in the folder names, if anonymization
            # has been run
            # loop through possible patient names, and find the match in this folder path
            for pctr, patient in enumerate(dt.patients):
                if patient in niiFolder:
                    part1 = niiFolder[:niiFolder.index(patient)]
                    part2 = niiFolder[niiFolder.index(patient) + len(patient):]
                    # find the key corresponding to this patient in the patientLookup dict
                    key_list = list(patientLookup.keys())
                    val_list = list(patientLookup.values())
                    key_ind = val_list.index(patient)
                    patientID = key_list[key_ind]
                    niiFolder = part1 + patientID + part2

            if not os.path.exists(niiFolder):
                os.makedirs(niiFolder)
            # write the nifti file for this folder
            # check for localizers etc first as these don't convert well to nifti
            if not any(x.lower() in folder.lower() for x in config['excludeNifti']):
                converter = Dcm2niix()
                converter.inputs.source_dir = folder
                converter.inputs.compression = 5
                converter.inputs.output_dir = niiFolder
                print('NIFTI output folder: %s' % converter.inputs.output_dir)
                converter.inputs.out_filename = '%p'
                # run the conversion
                try:
                    converter.run()
                    print('...Done!')
                except Exception as inst:
                    err = inst
                    err_txt = str(err)
                    if 'decompress with gdcmconv' in err_txt:

                        # loop through all files in dcmFolder, and decompress them
                        allFiles = os.listdir(folder)
                        for thisFile in allFiles:
                            try:
                                thisFileFullPath = os.path.join(folder, thisFile)
                                thisFileFullPath_out = os.path.join(folder, thisFile) # overwrites originals

                                ds = pydicom.read_file(thisFileFullPath, stop_before_pixels=True)
                                gdcmconv = subprocess.run(['gdcmconv', '-i', thisFileFullPath, '-o', thisFileFullPath_out, '-w'])
                            except Exception:
                                print('Unable to decompress file: %s' % thisFileFullPath)
                        # Now try dcm2niix again, on the decompressed files
                        try:
                            converter.run()
                        except Exception as inst:
                            print('Still unable to convert %s folder to NIFTI' % folder)










