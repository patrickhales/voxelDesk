.. _vxd_make_dicom:

============================================================
vxd_make_dicom.py
============================================================

Synopsis
------------
Create a new DICOM series from NIFTI data. An suitable *template* DICOM file must exist (see :ref:`Description`).

Usage
--------

.. code-block:: text

    vxd_make_dicom.py -t/--template <template DICOM file> -n/--nifti <source NIFTI file> [options]

- **-t**/**\--template**: path to the template DICOM file.
- **-n**/**\--nifti**: path to the source NIFTI file. This must be either a 3D or 4D NIFTI volume. If a 4D NIFTI volume
  is passed, it is assumed the NIFTI volume contains (R,G,B) values for each voxel, and the 4th dimension contains these values.

.. _Description:

Description
-------------
**vxd_make_dicom.py** will create a new DICOM series from an existing NIFTI file. The new DICOM series will be based on a
template DICOM file, which is provided via the **\-t** / **\--template** argument.
The criteria for a valid template file are as follows:

- The template file must be one file from an existing DICOM series (enhanced DICOMs are also accepted, in which
  the entire series is stored within a single file).
- For non-enhanced DICOMs, the rest of the DICOM files for this series must reside in the same folder as the template file.
- The NIFTI file should originate from the template DICOM series (i.e. the NIFTI file represents a NIFTI-conversion
  of the template DICOM series). *The only thing which can change between the NIFTI and DICOM series is the values stored in
  voxels themselves.* All other properties, such as the matrix size, image orientation etc, must be identical.

The intended use of **vxd_make_dicom.py** is for situations in which a raw DICOM series has first been converted into NIFTI
format, after which post-processing has been performed to generate new images. An example would be a processed track density image map, which uses a
scanner-generated Fractional Anisotropy image to provide the template DICOM header. **vxd_make_dicom.py** can be used
to generate a new DICOM series, using the existing DICOM template, and taking new voxel values from the processed NIFTI image. This works because the
source NIFTI data and the DICOM template are in the same "space".

To facilitate integration of the new DICOM series back into the patient's original study on a PACS system,
the DICOM tags in the new series are based on those from the template series, with only minor changes.
These changes include items such as the *SeriesDescription* and *SeriesInstanceUID* DICOM tags, but tags such as *ImageOrientationPatient*,
*ImagePositionPatient*, *Rows*, *Columns*, etc. remain un-changed.

.. warning::

    Do not use NIFTI files which have different orientations, matrix/voxel sizes, etc. from the template DICOM series.
    **It is only the values stored in the voxels themselves which can differ between the NIFTI and DICOM files.**

Options
---------

- **-c** / **\--cmap** *colourmap*:
  By default, the new DICOM series will use a greyscale colour scheme, unless a 4D NIFTI volume is provided, in which case
  it is assumed RGB values are held in the 4th dimension.
  However, colour DICOMs can also be written from a 3D source NIFTI file, by specifying a colourmap.
  Colour DICOMs created by voxelDesk are in 3-channel RGB format, with the DICOM tag *SamplesPerPixel* set to 3,
  and *PhotometricInterpretation* set to RGB. Colourmaps are taken from the *matplotlib* library, and the available colourmaps can be viewed
  `here <https://matplotlib.org/stable/tutorials/colors/colormaps.html>`_.

  |
- **-s** / **\--series_description** *new series description*:
  Option to define the series description for the new DICOM series. If not specified, the default is to use the series
  description from the template file, with the suffix '*-vxd*', or '*-vxd-rgb*' if a colour DICOM series is being created.


Example Usages
----------------

- Create a new DICOM series depicting track density images (stored in the file *cortico-spinal-tract-tdi.nii.gz*).
  Use the existing *dti-fa* DICOM series from the same study as the template for the new DICOM series.

  .. code-block::

    vxd_make_dicom.py --template path/to/dicomfolder/dti-fa-0001.dcm --nifti path/to/niftifolder/cortico-spinal-tract-tdi.nii.gz

  We didn't specify a name for the new series description, so assuming *dti-fa* was the series description of the template file,
  the new series will be named *dti-fa-vxd*.

  |
- As above, but this time we'll specify a series description for the new DICOM series (CST-TDI), and produce colour
  DICOM images, using the *jet* colourmap.

  .. code-block::

    vxd_make_dicom.py --template path/to/dicomfolder/dti-fa-0001.dcm --nifti path/to/niftifolder/cortico-spinal-tract-tdi.nii.gz --series_description CST-TDI --cmap jet





