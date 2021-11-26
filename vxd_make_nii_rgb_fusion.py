#!/usr/bin/env python

# function to create an RGB NIFTI file, consisting of one colour image overlaid on another background image.

import nibabel
from matplotlib import cm
from matplotlib.colors import ListedColormap
import numpy as np
import sys
from vxdTools.tidyAndNormalize import tidyAndNormalize
import argparse
import os

default_uthr_prc = 99.5
default_lthr_prc = 0
default_betfrac = 0.2
default_alpha = 0.25
default_colormap_fg = 'jet'
default_colormap_bg = 'gray'
default_cmap_res = 256
default_self_modulate = False
default_remove_zeros = False


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

    required.add_argument("-b", "--bg", required=True, help="Background NIFTI file")
    required.add_argument("-f", "--fg", required=True, help="Foreground NIFTI file")
    optional.add_argument("-cf", "--fg_cmap", required=False, help="Foreground colour map name (default: '%s')" % default_colormap_fg)
    optional.add_argument("-cb", "--bg_cmap", required=False, help="Background colour map name (default: '%s')" % default_colormap_bg)
    optional.add_argument("-a", "--alpha", required=False, help="Fixed foreground alpha value (0 to 1) (default: %0.2f)" % default_alpha)
    optional.add_argument("-m", "--mask", required=False, help="Alpha map")
    optional.add_argument("-s", "--smod", action='store_true', required=False, help="Use self-modulation of FG image for setting alpha values")
    optional.add_argument("-uthr", "--uthr", required=False, help="Upper percentile to use for image normalization. Default = %0.1f" % default_uthr_prc)
    optional.add_argument("-lthr", "--lthr", required=False, help="Lower percentile to use for image normalization. Default = %0.1f" % default_lthr_prc)
    optional.add_argument("-zx", "--zx", required=False, help="Convert negative values to zero", action='store_true')

    optional.add_argument('-h', '--help', action='help', help='Show this help message and exit')

    args = ap.parse_args()

    #  --- Foreground NIFTI file
    niiFile_fg = args.fg
    # check if user has passed full path or relative path to the input file
    if not os.path.isabs(niiFile_fg):
        wdir = os.getcwd()
        niiFileFullPath = os.path.join(wdir, niiFile_fg)
        niiFile_fg = niiFileFullPath
    if '.nii' not in niiFile_fg:
        print('Error: Foreground file does not appear to be a NIFTI file: %s' % niiFile_fg)
        print('Ensure filename following -f flag contains \'.nii\'')
        sys.exit(1)
    if not os.path.exists(niiFile_fg):
        print('Error: Foreground file cannot be found: %s' % niiFile_fg)
        print('Check filename/path')
        sys.exit(1)
    else:
        print('')
        print('- Foreground NIFTI File = %s' % (niiFile_fg))

    #  --- Background NIFTI file
    niiFile_bg = args.bg
    # check if user has passed full path or relative path to the input file
    if not os.path.isabs(niiFile_bg):
        wdir = os.getcwd()
        niiFileFullPath = os.path.join(wdir, niiFile_bg)
        niiFile_bg = niiFileFullPath
    if '.nii' not in niiFile_bg:
        print('Error: Background file does not appear to be a NIFTI file: %s' % niiFile_bg)
        print('Ensure filename following -b flag contains \'.nii\'')
        sys.exit(1)
    if not os.path.exists(niiFile_bg):
        print('Error: Background file cannot be found: %s' % niiFile_bg)
        print('Check filename/path')
        sys.exit(1)
    else:
        print('- Background NIFTI File = %s' % (niiFile_bg))

    #  --- Alpha mask NIFTI file
    if args.mask:
        niiFile_alphamask = args.mask
        # check if user has passed full path or relative path to the input file
        if not os.path.isabs(niiFile_alphamask):
            wdir = os.getcwd()
            niiFileFullPath = os.path.join(wdir, niiFile_alphamask)
            niiFile_alphamask = niiFileFullPath
        if '.nii' not in niiFile_alphamask:
            print('Error: Alpha mask file does not appear to be a NIFTI file: %s' % niiFile_alphamask)
            print('Ensure filename following -m/--mask flag contains \'.nii\'')
            sys.exit(1)
        if not os.path.exists(niiFile_alphamask):
            print('Error: Alpha mask file cannot be found: %s' % niiFile_alphamask)
            print('Check filename/path')
            sys.exit(1)
        else:
            print('- Alpha mask NIFTI File = %s' % (niiFile_alphamask))

    #  --- Foreground colour map
    if args.fg_cmap:
        user_colormap = args.fg_cmap
        # check the user has passed a recognized colormap
        if any(user_colormap.lower() in x.lower() for x in valid_cmaps):
            colormap_fg = user_colormap
        else:
            print('Error: User-specified colormap %s not recognized' % user_colormap)
            sys.exit(1)
    else:
        colormap_fg = default_colormap_fg

    #  --- Background colour map
    if args.bg_cmap:
        user_colormap = args.bg_cmap
        # check the user has passed a recognized colormap
        if any(user_colormap.lower() in x.lower() for x in valid_cmaps):
            colormap_bg = user_colormap
        else:
            print('Error: User-specified colormap %s not recognized' % user_colormap)
            sys.exit(1)
    else:
        colormap_bg = default_colormap_bg

    # --- user upper / lower percentile values for clipping
    # TODO: separate these out for FG and BG, if needed
    if args.uthr:
        user_uthr_prc = float(args.uthr)
        if user_uthr_prc < 0 or user_uthr_prc > 100:
            print('Error: Invalid upper percentile for clipping (%0.2f)' % user_uthr_prc)
            print('Values must be between 0 and 100')
            sys.exit(1)
        else:
            uthr_prc_fg = user_uthr_prc
            uthr_prc_bg = user_uthr_prc
    else:
        uthr_prc_fg = default_uthr_prc
        uthr_prc_bg = default_uthr_prc

    if args.lthr:
        user_lthr_prc = float(args.lthr)
        if user_lthr_prc < 0 or user_lthr_prc > 100:
            print('Error: Invalid lower percentile for clipping (%0.2f)' % user_lthr_prc)
            print('Values must be between 0 and 100')
            sys.exit(1)
        else:
            lthr_prc_fg = user_lthr_prc
            lthr_prc_bg = user_lthr_prc
    else:
        lthr_prc_fg = default_lthr_prc
        lthr_prc_bg = default_lthr_prc

    if uthr_prc_fg <= lthr_prc_fg or uthr_prc_bg <= lthr_prc_bg:
        print('Error: upper threshold for clipping (%0.2f) is lower than or equal to lower threshold (%0.2f)'
              % (uthr_prc_fg, lthr_prc_fg))
        sys.exit(1)

    # --- alpha value
    if args.alpha:
        user_alpha = float(args.alpha)
        if user_alpha < 0 or user_alpha > 1.0:
            print('Error: Invalid alpha value (%0.2f)' % user_alpha)
            print('Values must be between 0 and 1.0')
            sys.exit(1)
        else:
            alpha = user_alpha
    else:
        alpha = default_alpha

     # --- use foreground image to self-modulate alpha values
    if args.smod:
        self_modulate = True
    else:
        self_modulate = default_self_modulate

    # --- zero out negative voxels
    if args.zx:
        remove_zeros = True
    else:
        remove_zeros = default_remove_zeros


    colormap_res = default_cmap_res

    # load the nifti data
    nii = nibabel.load(niiFile_fg)
    fg = nii.get_fdata()
    nii = nibabel.load(niiFile_bg)
    bg = nii.get_fdata()

    # check to see if FG image is 3 channel RGB. If so this over-rides the fg colormap
    # get the dimensions
    ndim = np.ndim(fg)
    if ndim == 4:
        fg_rgb = True
    else:
        fg_rgb = False

    if bg.shape != fg.shape[0:3]:
        print('Error: FG dimensions %s do not match BG dimensions %s' % (fg.shape, bg.shape))
        sys.exit(1)
    if args.mask:
        nii_mask = nibabel.load(niiFile_alphamask)
        alphamap = nii_mask.get_fdata()
        if alphamap.shape != fg.shape[0:3]:
            print('Error: FG/BK dimensions %s do not match alpha map dimensions %s' % (fg.shape, alphamap.shape))
            sys.exit(1)
    else:
        # if no alpha map is specified, set all voxels to 1.0
        alphamap = np.ones(fg.shape[0:3])

    if ndim == 2:
        xres, yres = fg.shape

    if ndim == 3:
        xres, yres, zres = fg.shape

    if ndim == 4:
        xres, yres, zres, tres = fg.shape

    if ndim == 1 or ndim > 4:
        print('Error: input NIFTI file has incompatible dimensions')
        sys.exit(1)

    # clean the foreground and background data
    bg = tidyAndNormalize(bg, remove_zeros=remove_zeros, uthr_prc=uthr_prc_bg, lthr_prc=lthr_prc_bg)
    if not fg_rgb:
        fg = tidyAndNormalize(fg, remove_zeros=remove_zeros, uthr_prc=uthr_prc_fg, lthr_prc=lthr_prc_fg)
        fg_norm = tidyAndNormalize(fg, remove_zeros=remove_zeros, uthr_prc=uthr_prc_fg, lthr_prc=lthr_prc_fg, normalize=True)
    else:
        fg_norm = fg
        fg_max = np.max(fg, axis=3)
        fg_sum = np.sum(fg, axis=3)
        fg_sum_norm = tidyAndNormalize(fg_sum, remove_zeros=True, uthr_prc=100, lthr_prc=0, normalize=True)

    # ensure alphamap values range from 0 to 1
    alphamap = np.clip(alphamap, a_min=0, a_max=1.0)

    # load the colormaps
    cmap_fg = cm.get_cmap(colormap_fg, colormap_res)
    cmap_bg = cm.get_cmap(colormap_bg, colormap_res)

    # re-scale the data to range from 0 to cmap_res
    bg_rescaled = np.interp(bg, (bg.min(), bg.max()), (0, colormap_res)).astype(int)
    fg_rescaled = np.interp(fg, (fg.min(), fg.max()), (0, colormap_res)).astype(int)

    # Assign a new RGB triplet to each voxel (0 to 1). The fourth dimension will be alpha values, which will be ones as default
    bg_rgba = cmap_bg(bg_rescaled)
    if not fg_rgb:
        fg_rgba = cmap_fg(fg_rescaled)
    else:
        fg_rgba = np.ones((xres, yres, zres, 4))
        fg_rgba[:, :, :, 0:3] = fg_norm

    # multiply the alpha value by the alpha mask. This way, we can use a non-binary mask to have a variation in alpha values.
    # Or use a binary mask to keep a constant value of alpha throughout
    if self_modulate:
        if not fg_rgb:
            alphamap = fg_norm * alphamap
        else:
            alphamap = fg_sum_norm * alphamap
    else:
        alphamap = alpha * alphamap

    # The FG image may not cover the entire FOV of the background. If so, remove zero voxels from the FG image
    if not fg_rgb:
        alphamap[fg == 0] = 0
    else:
        pass
        #alphamap[fg_sum_norm < 0.1] = 0

    alphamap_inverse = 1 - alphamap

    # combine the fg and bg images into a fusion image.
    # We will blend the background image with the foreground image, with the ratios specified by the alphamap
    if not fg_rgb:
        extend_dim = ndim
    else:
        extend_dim = 3
    alphamap_rgb = np.repeat(np.expand_dims(alphamap, extend_dim), 3, axis=extend_dim)
    alphamap_inverse_rgb = np.repeat(np.expand_dims(alphamap_inverse, extend_dim), 3, axis=extend_dim)

    fusion_rgb = (fg_rgba[:, :, :, 0:3] * alphamap_rgb) + (bg_rgba[:, :, :, 0:3] * alphamap_inverse_rgb)

    # write out a new NIFTI file
    niiFileNoExt = niiFile_bg[:niiFile_bg.index('.nii')]
    outFile = niiFileNoExt + '_fusion.nii.gz'
    nibabel.save(nibabel.Nifti1Image(fusion_rgb, nii.affine, nii.header), outFile)
    print('- Output NIFTI File = %s' % (outFile))
    print('')
