# function to convert the raw values in a numpy array to RGB values, based on a given colormap

from vxdTools.tidyAndNormalize import tidyAndNormalize
from matplotlib import cm
from matplotlib.colors import ListedColormap
import sys
import numpy as np

default_scaling = 256
default_colormap = 'jet'
default_uthr_prc = 99.5
default_lthr_prc = 0
default_addBlack = True
default_remove_zeros = True

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


def array_to_rgb(dat, colormap=default_colormap, uthr_prc=default_uthr_prc, lthr_prc=default_lthr_prc,
                 remove_zeros=default_remove_zeros, scaling=default_scaling, addBlack=default_addBlack):


    cmap_res = 256

    # check the user has passed a recognized colormap
    if any(colormap.lower() in x.lower() for x in valid_cmaps):
        pass
    else:
        print('Error: User-specified colormap %s not recognized' % colormap)
        sys.exit(1)

    if lthr_prc < 0 or lthr_prc > 100:
        print('Error: Invalid lower percentile for clipping (%0.2f)' % lthr_prc)
        print('Values must be between 0 and 100')
        sys.exit(1)
    if uthr_prc < 0 or uthr_prc > 100:
        print('Error: Invalid upper percentile for clipping (%0.2f)' % uthr_prc)
        print('Values must be between 0 and 100')
        sys.exit(1)
    if uthr_prc <= lthr_prc:
        print('Error: upper threshold for clipping (%0.2f) is lower than or equal to lower threshold (%0.2f)'
              % (uthr_prc, lthr_prc))
        sys.exit(1)


    # clean the raw data
    dat = tidyAndNormalize(dat, remove_zeros=remove_zeros, uthr_prc=uthr_prc, lthr_prc=lthr_prc)

    cmap_base = cm.get_cmap(colormap, cmap_res)

    # extend the colormap, to make black the lowest value
    if addBlack:
        newcolors0 = cmap_base(np.linspace(0, 1, cmap_res - 1))
        rows, cols = newcolors0.shape
        newcolors = np.zeros((rows + 1, cols))
        # set the alpha for the black row to 1
        newcolors[0, 3] = 1.0
        newcolors[1:, :] = newcolors0
        cmap = ListedColormap(newcolors)
    else:
        cmap = cmap_base

    # re-scale dat to range from 0 to maxval
    dat_rescaled = np.interp(dat, (dat.min(), dat.max()), (0, cmap_res)).astype(int)

    # Assign a new RGBA vector to each voxel
    dat_rgba = cmap(dat_rescaled)

    # remove the alpha values..
    # get the dimensions
    ndim = np.ndim(dat)

    if ndim == 2:
        dat_rgb = dat_rgba[:, :, 0:3]
    if ndim == 3:
        dat_rgb = dat_rgba[:, :, :, 0:3]
    if ndim == 4:
        dat_rgb = dat_rgba[:, :, :, :, 0:3]

    if ndim == 1 or ndim > 4:
        print('Error: input NIFTI file has incompatible dimensions')
        sys.exit(1)

    return dat_rgb * scaling

