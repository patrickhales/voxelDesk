#!/usr/bin/env python

"""
Function to remove outliers from a nifti file (based on clipping at min/max percentile values), and normalize signal
intensity between 0 to 1
"""
import nibabel
import argparse
import os
import sys
from vxdTools.tidyAndNormalize import tidyAndNormalize
from termcolor import colored

if __name__ == '__main__':

    uprc_thr_default = 99.9
    lprc_thr_default = 0.1

    # Construct the argument parser
    ap = argparse.ArgumentParser(add_help=False)

    # Add the arguments to the parser
    required = ap.add_argument_group('required arguments')
    optional = ap.add_argument_group('optional arguments')

    required.add_argument("-i", "--input", required=True, help="Input NIFTI file")
    required.add_argument("-o", "--output", required=True, help="Output NIFTI file")
    optional.add_argument("-n", "--nonorm", required=False, action='store_true', help="Do not normalize image")
    optional.add_argument("-z", "--keepneg", required=False, action='store_true', help="Retain negative values")
    optional.add_argument("-u", "--uthr", required=False, help="Upper percentile to use for clipping")
    optional.add_argument("-l", "--lthr", required=False, help="Lower percentile to use for clipping")
    optional.add_argument('-h', '--help', action='help', help='Show this help message and exit')

    args = ap.parse_args()

    #  --- Source NIFTI file
    niiFile = args.input
    # check if user has passed full path or relative path to the input file
    if not os.path.isabs(niiFile):
        wdir = os.getcwd()
        niiFileFullPath = os.path.join(wdir, niiFile)
        niiFile = niiFileFullPath
    if '.nii' not in niiFile:
        print(colored(f'Error: Input file does not appear to be a NIFTI file: {niiFile}', 'red'))
        sys.exit(1)
    if not os.path.exists(niiFile):
        print(colored(f'Error: Input file cannot be found: {niiFile}', 'red'))
        sys.exit(1)
    else:
        print('')
        print('- Source NIFTI File: %s' % (niiFile))

        #  --- Output NIFTI file
        outFile = args.output
        # check if user has passed full path or relative path to the input file
        if not os.path.isabs(outFile):
            wdir = os.getcwd()
            outFileFullPath = os.path.join(wdir, outFile)
            outFile = outFileFullPath
        if '.nii' not in outFile:
            # append '.nii.gz' to outFile if not already passed
            outFileFullPath += '.nii.gz'
            outFile = outFileFullPath

        print('- Output NIFTI File: %s' % (outFile))

    if args.nonorm:
        normalize = False
    else:
        normalize = True

    if args.keepneg:
        remove_zeros = False
    else:
        remove_zeros = True

    if args.uthr:
        uthr_prc = float(args.uthr)
        if uthr_prc < 0 or uthr_prc > 100:
            print(colored(f'Error: invalid value for clipping upper percentile: {uthr_prc}', 'red'))
            sys.exit(1)
    else:
        uthr_prc = uprc_thr_default

    if args.lthr:
        lthr_prc = float(args.lthr)
        if lthr_prc < 0 or lthr_prc > 100:
            print(colored(f'Error: invalid value for clipping lower percentile: {lthr_prc}', 'red'))
            sys.exit(1)
    else:
        lthr_prc = lprc_thr_default
    if (uthr_prc <= lthr_prc):
        print(colored(f'Error: invalid range for clipping percentile: {lthr_prc} to {uthr_prc}', 'red'))
        sys.exit(1)

    print('- Clipping range: %.2f to %.2f percentile' % (lthr_prc, uthr_prc))
    if normalize:
        print('- Applying signal normalization...')
    if remove_zeros:
        print('- Zeroing negative values...')

    # Open the source NIFTI file
    nii = nibabel.load(niiFile)
    dat = nii.get_fdata()
    # Apply normalization and tidying
    datnorm = tidyAndNormalize(dat, normalize=normalize, remove_zeros=remove_zeros, uthr_prc=uthr_prc, lthr_prc=lthr_prc)
    # Write the output
    nibabel.save(nibabel.Nifti1Image(datnorm, nii.affine, nii.header), outFile)
    print('...done')
    print(' ')

