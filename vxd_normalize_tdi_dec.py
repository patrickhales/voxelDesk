#!/usr/bin/env python

import nibabel
import numpy as np
import os
from vxdTools.tidyAndNormalize import tidyAndNormalize
import argparse
import sys
from termcolor import colored

if __name__ == '__main__':

    uprc_thr_default = 99.9
    lprc_thr_default = 0.1

    # Construct the argument parser
    ap = argparse.ArgumentParser(add_help=False)

    # Add the arguments to the parser

    required = ap.add_argument_group('required arguments')
    optional = ap.add_argument_group('optional arguments')

    required.add_argument("-d", "--dec", required=True, help="TDI DEC NIFTI file")
    required.add_argument("-g", "--grey", required=True, help="TDI grayscale NIFTI file")
    optional.add_argument("-o", "--out", required=False, help="Output NIFTI filename")
    optional.add_argument("-u", "--uthr", required=False, help="Upper percentile to use for clipping")
    optional.add_argument("-l", "--lthr", required=False, help="Lower percentile to use for clipping")

    optional.add_argument('-h', '--help', action='help', help='Show this help message and exit')

    args = ap.parse_args()

    # Input TDI DEC file
    tdiFile = args.dec
    # check if user has passed full path or relative path to the input file
    if not os.path.isabs(tdiFile):
        wdir = os.getcwd()
        niiFileFullPath = os.path.join(wdir, tdiFile)
        tdiFile = niiFileFullPath
    if '.nii' not in tdiFile:
        print('Error: Foreground file does not appear to be a NIFTI file: %s' % tdiFile)
        print('Ensure filename following -d flag contains \'.nii\'')
        sys.exit(1)
    if not os.path.exists(tdiFile):
        print('Error: TDI DEC file cannot be found: %s' % tdiFile)
        print('Check filename/path')
        sys.exit(1)
    else:
       pass

    # Input TDI greyscale file
    tdiMagFile = args.grey
    # check if user has passed full path or relative path to the input file
    if not os.path.isabs(tdiMagFile):
        wdir = os.getcwd()
        niiFileFullPath = os.path.join(wdir, tdiMagFile)
        tdiMagFile = niiFileFullPath
    if '.nii' not in tdiMagFile:
        print('Error: TDI greyscale file does not appear to be a NIFTI file: %s' % tdiMagFile)
        print('Ensure filename following -g flag contains \'.nii\'')
        sys.exit(1)
    if not os.path.exists(tdiMagFile):
        print('Error: TDI greyscale file cannot be found: %s' % tdiMagFile)
        print('Check filename/path')
        sys.exit(1)
    else:
        pass

    # Optional Outfile name
    if args.out:
        outFile = args.out
        # check if user has passed full path or relative path to the file
        if not os.path.isabs(outFile):
            wdir = os.getcwd()
            niiFileFullPath = os.path.join(wdir, outFile)
            outFile = niiFileFullPath
        if '.nii' not in outFile:
            outFile = outFile + '.nii.gz'
    else:
        outFile = tdiFile[0:tdiFile.index('.nii')] + '_norm' + tdiFile[tdiFile.index('.nii'):]


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


    print(' ')
    print('- TDI DEC File:\t\t%s' % tdiFile)
    print('- TDI Greyscale File:\t%s' % tdiMagFile)
    print('- Output File:\t\t%s' % outFile)
    print(' ')


    # load the RGB TDI DEC data
    nii = nibabel.load(tdiFile)
    dec = nii.get_fdata()

    # load the magnitude TDI data
    nii2 = nibabel.load(tdiMagFile)
    mag = nii2.get_fdata()
    mag_filt = tidyAndNormalize(mag, normalize=False, remove_zeros=True, uthr_prc=uthr_prc, lthr_prc=lthr_prc)
    mag_norm = tidyAndNormalize(mag_filt, normalize=True, remove_zeros=True, uthr_prc=100, lthr_prc=0)

    # calc the sum of the RGB values in each voxel
    dec_sum = dec.sum(axis=3)
    dec_max = dec.max(axis=3)

    # Normalize the RGB values to range from 0 to 1 in each voxel, if not already done so
    # (note vecreg normalizes the RGB values for you)
    if dec_max.max() > 1.0:
        dec_norm = np.zeros(dec.shape)
        for i in range(3):
            dec_norm[:, :, :, i] = dec[:, :, :, i] / mag_filt
        dec_norm[np.isnan(dec_norm)] = 0
        dec_norm[np.isinf(dec_norm)] = 0
    else:
        dec_norm = dec

    # modulate the normalized RGB values by the normalized greyscale TDI image, so that RGB brightness reflects TDI
    dec_norm_mod = np.zeros(dec.shape)
    for i in range(3):
        dec_norm_mod[:, :, :, i] = dec_norm[:, :, :, i] * mag_norm

    # write out the dec_norm_mod file
    nibabel.save(nibabel.Nifti1Image(dec_norm_mod, nii.affine, nii.header), outFile)
