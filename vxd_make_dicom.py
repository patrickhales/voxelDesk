#!/usr/bin/env python

from vxdDicom.readDicomVolume import readDicomVolume
from vxdTools.adapt_dicom_uid import adapt_dicom_uid
from vxdTools.safeName import safeName
from vxdDicom.create_new_dicom_volume import create_new_dicom_volume
import pydicom
from pydicom.filereader import InvalidDicomError
import sys
import os
import ntpath
import nibabel
import argparse
import numpy as np

default_SeriesDescription = 'voxelDesk_dicom'

valid_cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis',
               'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
               'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
               'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
               'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
               'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
               'hot', 'afmhot', 'gist_heat', 'copper',
               'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
               'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
               'twilight', 'twilight_shifted', 'hsv',
               'Pastel1', 'Pastel2', 'Paired', 'Accent',
               'Dark2', 'Set1', 'Set2', 'Set3',
               'tab10', 'tab20', 'tab20b', 'tab20c',
               'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
               'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
               'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar']


if __name__ == '__main__':

    # Construct the argument parser
    ap = argparse.ArgumentParser(add_help=False)

    # Add the arguments to the parser

    required = ap.add_argument_group('required arguments')
    optional = ap.add_argument_group('optional arguments')

    required.add_argument("-t", "--template", required=True, help="Template DICOM file")
    optional.add_argument("-n", "--nifti", required=False, help="Source NIFTI file for new image data")
    optional.add_argument("-c", "--cmap", required=False, help="Colour map name")
    optional.add_argument("-s", "--series_description", required=False, help="Series description")
    optional.add_argument('-h', '--help', action='help', help='Show this help message and exit')


    args = ap.parse_args()

    # --- Template DICOM file (required)
    templateFile = args.template
    # check if user has passed full path or relative path to the input file
    if not os.path.isabs(templateFile):
        wdir = os.getcwd()
        templateFileFullPath = os.path.join(wdir, templateFile)
        templateFile = templateFileFullPath

    #  --- Source NIFTI file
    if args.nifti:
        niiSourceFile = args.nifti
        # check if user has passed full path or relative path to the input file
        if not os.path.isabs(niiSourceFile):
            wdir = os.getcwd()
            niiFileFullPath = os.path.join(wdir, niiSourceFile)
            niiSourceFile = niiFileFullPath
        if '.nii' not in niiSourceFile:
            print('Error: Input file does not appear to be a NIFTI file: %s' % niiSourceFile)
            print('Ensure filename following -i flag contains \'.nii\'')
            sys.exit(1)
        if not os.path.exists(niiSourceFile):
            print('Error: Input file cannot be found: %s' % niiSourceFile)
            print('Check filename/path')
            sys.exit(1)
        else:
            print('')
            print('- Source NIFTI File: %s' % (niiSourceFile))
            # read the nifti volume
            nii = nibabel.load(niiSourceFile)

    else:
        niiSourceFile = None
        nii = None

    # --- Colormap
    if args.cmap:
        user_colormap = args.cmap
        # check the user has passed a recognized colormap
        if any(user_colormap.lower() in x.lower() for x in valid_cmaps):
            colormap = user_colormap
            rgb_flag = True
        else:
            print('Error: User-specified colormap %s not recognized' % user_colormap)
            sys.exit(1)
    else:
        colormap = None
        rgb_flag = False

    # --- Series Description
    if args.series_description:
        newSeriesDescription = safeName(args.series_description)
    else:
        newSeriesDescription = None

    # check templateFile is a valid DICOM file
    try:
        ds = pydicom.read_file(templateFile, stop_before_pixels=True)
        if 'SeriesInstanceUID' in ds:
            templateSeriesInstanceUID = ds.SeriesInstanceUID
        else:
            print('Error: SeriesInstanceUID could not be identified from template DICOM file')
            sys.exit(1)

        if 'StudyInstanceUID' in ds:
            templateStudyInstanceUID = ds.StudyInstanceUID
        else:
            print('Error: StudyInstanceUID could not be identified from template DICOM file')
            sys.exit(1)

        if 'SeriesDescription' in ds:
            templateSeriesDescription = ds.SeriesDescription
        else:
            templateSeriesDescription = default_SeriesDescription

        # create a new SeriesInstanceUID
        if 'SeriesInstanceUID' in ds:
            uid = ds.SeriesInstanceUID
            newSeriesInstanceUID = adapt_dicom_uid(uid)
        else:
            newSeriesInstanceUID = pydicom.uid.generate_uid()

        if 'SeriesNumber' in ds:
            templateSeriesNumber = ds.SeriesNumber
        else:
            templateSeriesNumber = 0

    except (IOError, os.error) as why:
        print('Error: Could not open template DICOM file: %s' % templateFile)
        sys.exit(1)
    except InvalidDicomError:
        print('Error: Could not open template DICOM file: %s' % templateFile)
        sys.exit(1)
    except KeyError:
        print('Error: Could not open template DICOM file: %s' % templateFile)
        sys.exit(1)

    # read the dicom volume for this template file (assuming the full set of dicom files reside in the parent folder)
    print('- Template DICOM File: %s' % templateFile)
    dcm = readDicomVolume(templateFile)

    # Open the NIFTI volume (if passed), see if it contains RGB data (4th dimension), and check it is compatible with
    # the DICOM volume
    if nii is not None:
        # get info about the nifti data array, and check the dimensions are consistent with the dicom data
        # remember nifti data is stored in RAS+ format, dicom slices can be stored in any format
        if nii.ndim < 2 or nii.ndim > 4:
            print('Error: nii data should have between 2-4 dimensions. Passed nii has %d dimensions' % nii.ndim)
            sys.exit(1)
        else:
            nrows_nii = nii.shape[0]
            ncols_nii = nii.shape[1]
            if nii.ndim == 2:
                nSlices_nii = 1
            else:
                nSlices_nii = nii.shape[2]
            if nii.ndim == 4:
                nt_nii = nii.shape[3]
            else:
                nt_nii = None

        total_dicom_voxels = dcm.nRows * dcm.nCols * dcm.nSlices
        if nii.ndim == 4:
            total_nifti_voxels = np.prod(nii.shape[0:3])  # don't include 4th dimension (RGB values) in total no. voxels
        else:
            total_nifti_voxels = np.prod(nii.shape)

        if total_dicom_voxels != total_nifti_voxels:
            print('Error: dicom series and nifti data have incompatible sizes')
            print('Dicom dimensions: %d x %d x %d' % (dcm.nRows, dcm.nCols, dcm.nSlices))
            print('NIFTI dimensions: %d x %d x %d' % (nrows_nii, ncols_nii, nSlices_nii))
            sys.exit(1)

        # if the nifti data is 4D, we'll assume the 4th dimension gives RGB values
        if nt_nii is not None:
            if nt_nii != 3:
                print('Error: 4D NIFTI arrays should contain a 3-element RGB vector in the 4th dimension')
                print('The NIFTI data passed has size %d in the 4th dimension' % nt_nii)
                sys.exit(1)
            else:
                rgb_flag = True
                print('- Using RGB data from 4D NIFTI file')


    # create new set of DICOM tags

    if rgb_flag:
        out_suffix = '-vxd-rgb'
    else:
        out_suffix = '-vxd'

    if newSeriesDescription is None:
        outFolder = dcm.dcmFolder + out_suffix
        newSeriesDescription = templateSeriesDescription + out_suffix
    else:
        if templateSeriesNumber < 10:
            newSeriesNumberStr = '00' + str(templateSeriesNumber)
        if templateSeriesNumber >= 10 and templateSeriesNumber < 100:
            newSeriesNumberStr = '0' + str(templateSeriesNumber)
        if templateSeriesNumber >= 100:
            newSeriesNumberStr = str(templateSeriesNumber)

        dcmFolder_parent, dcmFolder = ntpath.split(dcm.dcmFolder)
        outFolder = os.path.join(dcmFolder_parent, newSeriesNumberStr + '-' + newSeriesDescription)

    print('- Output Folder: %s' % outFolder)
    if colormap is not None:
        print('- Colour map: %s' % colormap)
    else:
        if not rgb_flag:
            print('- Colour map: greyscale')

    newDcmTags = {'SeriesDescription': newSeriesDescription,
                  'SeriesInstanceUID': newSeriesInstanceUID
                  }

    create_new_dicom_volume(dcm, nii, outFolder, colormap=colormap, newDcmTags=newDcmTags)







