#!/usr/bin/env python

# function to create RGB versions of existing NIFTI files, using a given colour palette

import nibabel
from matplotlib import cm
from matplotlib.colors import ListedColormap
import numpy as np
import sys
from vxdTools.tidyAndNormalize import tidyAndNormalize
from vxdTools.automask import automask
import argparse
import os

# defaults
default_uthr_prc = 99.5
default_lthr_prc = 0
default_betfrac = 0.2
default_colormap = 'jet'
default_cmap_res = 256
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

    required.add_argument("-i", "--input", required=True, help="Input NIFTI file")
    optional.add_argument("-c", "--cmap", required=False, help="Colour map name (default: '%s')" % default_colormap)
    optional.add_argument("-b", "--black", required=False, help="Assign lowest values to black", action='store_true')
    optional.add_argument("-m", "--mask", required=False, help="Apply automated brain masking", action='store_true')
    optional.add_argument("-mf", "--mf", required=False, help="Fractional intensity threshold for use in brain mask")
    optional.add_argument("-zx", "--zx", required=False, help="Convert negative values to zero", action='store_true')
    optional.add_argument("-uthr", "--uthr", required=False, help="Upper percentile to use for image normalization. Default = %0.1f" % default_uthr_prc)
    optional.add_argument("-lthr", "--lthr", required=False, help="Lower percentile to use for image normalization. Default = %0.1f" % default_lthr_prc)
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
        print('Error: Input file does not appear to be a NIFTI file: %s' % niiFile)
        print('Ensure filename following -i flag contains \'.nii\'')
        sys.exit(1)
    if not os.path.exists(niiFile):
        print('Error: Input file cannot be found: %s' % niiFile)
        print('Check filename/path')
        sys.exit(1)
    else:
        print('')
        print('- Source NIFTI File = %s' % (niiFile))

    # --- Colormap
    if args.cmap:
        user_colormap = args.cmap
        # check the user has passed a recognized colormap
        if any(user_colormap.lower() in x.lower() for x in valid_cmaps):
            colormap = user_colormap
        else:
            print('Error: User-specified colormap %s not recognized' % user_colormap)
            sys.exit(1)
    else:
        colormap = default_colormap

    # --- Add black
    if args.black:
        add_black = True
    else:
        add_black = False

    # --- Auto-mask
    if args.mask:
        apply_mask = True
    else:
        apply_mask = False

    # --- Set fractional intensity threshold if using auto-mask
    if args.mf:
        user_betfrac = float(args.mf)
        if user_betfrac < 0 or user_betfrac > 1.0:
            print('Error: Invalid BET fractional intensity threshold (%0.2f)' % user_betfrac)
            print('Values must be between 0 and 1.0')
            sys.exit(1)
        else:
            betfrac = user_betfrac
    else:
        betfrac = default_betfrac

    # --- user upper / lower percentile values for clipping
    if args.uthr:
        user_uthr_prc = float(args.uthr)
        if user_uthr_prc < 0 or user_uthr_prc > 100:
            print('Error: Invalid upper percentile for clipping (%0.2f)' % user_uthr_prc)
            print('Values must be between 0 and 100')
            sys.exit(1)
        else:
            uthr_prc = user_uthr_prc
    else:
        uthr_prc = default_uthr_prc

    if args.lthr:
        user_lthr_prc = float(args.lthr)
        if user_lthr_prc < 0 or user_lthr_prc > 100:
            print('Error: Invalid lower percentile for clipping (%0.2f)' % user_lthr_prc)
            print('Values must be between 0 and 100')
            sys.exit(1)
        else:
            lthr_prc = user_lthr_prc
    else:
        lthr_prc = default_lthr_prc

    if uthr_prc <= lthr_prc:
        print('Error: upper threshold for clipping (%0.2f) is lower than or equal to lower threshold (%0.2f)'
              % (uthr_prc, lthr_prc))
        sys.exit(1)

    if args.zx:
        remove_zeros = True
    else:
        remove_zeros = False



    cmap_res = default_cmap_res

    # load the nifti data
    nii = nibabel.load(niiFile)
    dat = nii.get_fdata()

    # get the dimensions
    ndim = np.ndim(dat)

    if ndim == 2:
        xres, yres = dat.shape

    if ndim == 3:
        xres, yres, zres = dat.shape

    if ndim == 4:
        xres, yres, zres, tres = dat.shape

    if ndim == 1 or ndim > 4:
        print('Error: input NIFTI file has incompatible dimensions')
        sys.exit(1)

    # if requested, apply a brain mask
    if apply_mask:
        mask, maskFile = automask(niiFile, deleteFiles=True, betfrac=betfrac)
        if ndim < 4:
            dat = dat * mask
        else:
            for t in range(tres):
                dat[:, :, :, t] = dat[:, :, :, t] * mask

    # clean the raw data
    dat = tidyAndNormalize(dat, remove_zeros=remove_zeros, uthr_prc=uthr_prc, lthr_prc=lthr_prc)

    cmap_base = cm.get_cmap(colormap, cmap_res)

    # extend the colormap, to make black the lowest value
    if add_black:
        newcolors0 = cmap_base(np.linspace(0, 1, cmap_res-1))
        rows, cols = newcolors0.shape
        newcolors = np.zeros((rows+1, cols))
        # set the alpha for the black row to 1
        newcolors[0, 3] = 1.0
        newcolors[1:, :] = newcolors0
        cmap = ListedColormap(newcolors)
    else:
        cmap = cmap_base

    # re-scale dat to range from 0 to cmap_res
    dat_rescaled = np.interp(dat, (dat.min(), dat.max()), (0, cmap_res)).astype(int)


    # Assign a new RGB triplet to each voxel
    dat_rgb0 = cmap(dat_rescaled)
    # remove the alpha values (for output to 4D NIFTI)
    dat_rgb = dat_rgb0[:, :, :, 0:3]

    # write out a new NIFTI file
    niiFileNoExt = niiFile[:niiFile.index('.nii')]
    outFile = niiFileNoExt + '_RGB.nii.gz'
    nibabel.save(nibabel.Nifti1Image(dat_rgb, nii.affine, nii.header), outFile)
    print('- Output NIFTI File = %s' % (outFile))
    print('')

