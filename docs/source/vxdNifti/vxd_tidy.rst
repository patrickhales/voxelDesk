.. _vxd_tidy:

============================================================
vxd_tidy.py
============================================================

Synopsis
------------
Remove outliers from a NIFTI dataset (based on clipping at min/max percentile values), and normalize signal
intensities between 0 to 1.

Usage
--------
.. code-block:: text

    vxd_tidy.py -i/--input <source NIFTI file> -o/--output <output NIFTI file> [options]

- **-i** / **\--input**: the source NIFTI file.
- **-o** / **\--output**: the output NIFTI file.

Description
-------------
**vxd_tidy.py** provides a means to clip 'outliers' in a NIFTI dataset, such as spuriously high or low signal intensity values.
It also provides a quick means for normalizing a dataset, such that signal intensities are scaled between 0-1.

Options
---------
- **-n** / **\--nonorm**:
  Flag to disable signal intensity normalization. By default, signal intensity values will be normalized between 0-1
  in the output NIFTI file. Apply this flag to disable this feature.

  |
- **-z** / **\--keepneg**:
  Flag to retain negative signal intensity values. By default, negative signal intensity values will be clipped to 0.
  Apply this flag to retain negative values.

  |
- **-uthr** *percentile value (0-100)*:
  Option to specify the upper percentile value which will be used for clipping (default is 99.5).
  The source NIFTI data will be tidied to remove any outlying high or low values, as
  these can stretch the dynamic range in an un-wanted way. Any high signal intensity values above the **uthr** percentile
  value will be clipped to this value. Setting **uthr** to 100 stops any clipping being applied to high signal intensity values.

  |
- **-lthr** *percentile value (0-100)*:
  Option to specify the lower percentile value which will be used for clipping (default is 0).
  The source NIFTI data will be tidied to remove any outlying high or low values, as
  these can stretch the dynamic range in an un-wanted way. Any low signal intensity values below the **lthr** percentile
  value will be clipped to this value. Setting **lthr** to 0 stops any clipping being applied to low signal intensity values.

Example Usages
----------------

- Take an input NIFTI file (*t1_brain.nii.gz*), and normalize the signal intensity values between 0-1. We will also
  clip any values which exceed the 95% percentile of signal intensities in the dataset:

  .. code-block:: text

    vxd_tidy.py -i t1_brain.nii.gz -o t1_brain_tidied.nii.gz -uthr 95

