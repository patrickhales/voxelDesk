.. _vxd_make_nii_rgb:

============================================================
vxd_make_nii_rgb.py
============================================================

Synopsis
------------
Create a colour version of an existing NIFTI file, based on a specified colour palette.

Usage
--------
.. code-block:: text

    vxd_make_nii_rgb.py -i/--input <source NIFTI file> [options]

- **-i**/**\--input**: path to the source NIFTI file. The data can be 2D, 3D or 4D.


Description
-------------
**vxd_make_nii_rgb.py** will take an existing NIFTI dataset, and create a colour version of it. This is achieved by
appending an additional dimension to the dataset, which provides a (red,green,blue) triplet for each voxel.
RGB values are scaled between 0-1, and values are determined based on a given colourmap, specified
using the **-c**/**\--cmap** option (see below - 'jet' is the default).

A new NIFTI file is written, using the same filename as the source file, with an '_rgb' suffix.

Options
---------

- **-c** / **\--cmap** *colourmap*:
  Option to specify which colourmap is used to determine the (R,G,B) values (default is jet).
  Colourmaps are taken from the *matplotlib* library, and the available colourmaps can be viewed
  `here <https://matplotlib.org/stable/tutorials/colors/colormaps.html>`_.

  |
- **-b** / **\--black**:
  Flag to set the lowest values in the source NIFTI dataset to appear as black (regardless of the colourmap used).
  This can be useful for creating a black background when, for example, all non-tissue voxels have been set to have
  a value of zero.

  |
- **-m** / **\--mask**:
  Flag to create and apply a brain mask to the input NIFTI images, using FSL's `bet <https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/BET>`_
  algorithm (requires an existing FSL installation). This can be useful for brain images, to stop colourmaps being applied to
  the background noise (particularly if combined with the **-b** / **\--black** flag).

  |
- **-mf** *fractional intensity threshold (0-1)*:
  Option to specify the fractional intensity threshold used in the FSL BET brain extraction, if the **-m** / **\--mask** flag is applied.
  The default is 0.5, and smaller values give larger brain outline estimates.

  |
- **-zx**:
  Flag to convert negative values in the source NIFTI dataset to zero, prior to applying the colourmap.
  This helps to remove spurious negative values which might stretch the dynamic range in an un-wanted way.

  |
- **-uthr** *percentile value (0-100)*:
  Option to specify the upper percentile value which will be used for clipping (default is 99.5).
  Prior to applying the colourmap, the source NIFTI data will be tidied to remove any outlying high or low values, as
  these can stretch the dynamic range in an un-wanted way. Any high signal intensity values above the **uthr** percentile
  value will be clipped to this value. Setting **uthr** to 100 stops any clipping being applied to high signal intensity values.

  |
- **-lthr** *percentile value (0-100)*:
  Option to specify the lower percentile value which will be used for clipping (default is 0).
  Prior to applying the colourmap, the source NIFTI data will be tidied to remove any outlying high or low values, as
  these can stretch the dynamic range in an un-wanted way. Any low signal intensity values below the **lthr** percentile
  value will be clipped to this value. Setting **lthr** to 0 stops any clipping being applied to low signal intensity values.


Example Usages
----------------
- Create a colour version of the *test.nii.gz* file, using the 'hot' colourmap:

  .. code-block:: text

    vxd_make_nii_rgb.py -i test.nii.gz -c hot

  This will write a new file called *test_rgb.nii.gz*, with (R,G,B) values for each voxel.

  |
- Create a colour version of the *t1_brain.nii.gz* file, using the 'plasma' colourmap. Use a brain mask to ensure the signal
  in voxels outside of the brain is set to zero, and use a black background for these non-brain voxels:

  .. code-block:: text

    vxd_make_nii_rgb.py -i t1_brain.nii.gz -c plasma -m -b








