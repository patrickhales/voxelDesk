============================================================
vxd_make_nii_rgb_fusion.py
============================================================

Synopsis
------------
Performs a similar function to :ref:`vxd_make_nii_rgb`, but creates a fusion image of two NIFTI datasets, comprising
a foreground image overlaid on a background image. Different colourmaps can be used for each.

Usage
--------
.. code-block::

    vxd_make_nii_rgb_fusion.py -b/--bg <background NIFTI file> -f/--fg <foreground NIFTI file> [options]

- **-b** / **\--bg**: the background NIFTI file.
- **-f** / **\--fg**: the foreground NIFTI file.


Description
-------------
**vxd_make_nii_rgb_fusion.py** provides a means of creating a colour NIFTI dataset, which, similar to :ref:`vxd_make_nii_rgb`,
appends an additional dimension to the dataset, to provide a (red,green,blue) triplet for each voxel.

**vxd_make_nii_rgb_fusion.py** extends the functionality of :ref:`vxd_make_nii_rgb`, by allowing a foreground image
to be overlaid onto a background image. The transparency of the overlay, and the colourmaps used for the foreground and
background images, can be chosen by the user.

.. warning::
    The image dimensions of the foreground and background images must be identical.

A new colour NIFTI file is written, using the same filename as the background source file, with an '_fusion' suffix.
The fusion of these two images is 'burnt in' to the resulting NIFTI file. This new NIFTI file could be used to as the
source data to create a new colour DICOM series if desired (with the colour information already 'burnt in'), using
:ref:`vxd_make_dicom`.

Options
---------

- **-fg** / **\--fg_cmap** *colourmap*:
  Option to specify which colourmap is used to determine the (R,G,B) values of the foreground image (default is *jet*).
  Colourmaps are taken from the *matplotlib* library, and the available colourmaps can be viewed
  `here <https://matplotlib.org/stable/tutorials/colors/colormaps.html>`_.

  |
- **-bg** / **\--bg_cmap** *colourmap*:
  Option to specify which colourmap is used to determine the (R,G,B) values of the background image (default is *gray*).

  |
- **-a** / **\--alpha** *alpha value (0-1)*:
  Option to specify the alpha (transparency) value to be used for the foreground image. Values can range  0 (fully transparent),
  to 1.0 (fully opaque). The default is 0.25.

  |
- **-m** / **\--mask** *alpha mask NIFTI file*:
  Option to specify a third NIFTI file, which contains a map of alpha values to be applied to the foreground image.
  This allows transparency to vary across the foreground image, according to user-defined map of alpha values. This could
  be a binary mask, or continuous values between 0-1. If the **-a** / **\--alpha** option has also been used, the 'global'
  alpha value will be multiplied by the values in the alpha map.

  The dimensions of the alpha map NIFTI dataset must match the dimensions of the foreground and background images.

  |
- **-s** / **\--smod**:
  Flag to use *self-modulation* of the alpha values for the foreground image, using signal intensity values from the
  foreground image itself. This will scale the transparency of the foreground image according to the relative strength of
  signal in the foreground image. High signal areas will appear more opaque, and low signal areas will appear more transparent.
  Useful for when only hyper-intense regions in the foreground image are of interest.

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

.. note::
    The **uthr** and **lthr** clipping values are applied to both the foreground and background images simultaneously.
    If different clipping thresholds are required for each, apply :ref:`vxd_tidy` to these files individually, before using
    **vxd_make_nii_rgb_fusion.py**.

- **-zx**:
  Flag to convert negative values in the source NIFTI datasets to zero, prior to applying the colourmaps.
  This helps to remove spurious negative values which might stretch the dynamic range in an un-wanted way.


Example Usages
----------------

- Overlay a track density image (TDI.nii.gz) onto a background T1 image (t1_brain.nii.gz). We'll keep the background
  as grayscale, and use the *Reds* colourmap for the foreground:

  .. code-block::

    vxd_make_nii_rgb_fusion.py -fg TDI.nii.gz -bg t1_brain.nii.gz --fg_cmap Reds

  This will create a new NIFTI file called *t1_brain_fusion.nii.gz* with the fused images.

  |
- Overlay a colour cerebral blood flow image (CBF.nii.gz) onto a background T1 image (t1_brain.nii.gz) in a brain tumour patient.
  We'll keep the background as grayscale, and use the *hot* colourmap for the foreground. In addition, we will use a binary mask of
  the tumour as the alpha map, in order to only show the colour CBF overlay in the tumour region. Alpha values in this region will be set to 0.5.

  .. code-block::

    vxd_make_nii_rgb_fusion.py -fg CBF.nii.gz -bg t1_brain.nii.gz --fg_cmap hot --mask tumour_mask.nii.gz --alpha 0.5



