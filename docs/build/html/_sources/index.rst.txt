.. voxelDesk documentation master file, created by
   sphinx-quickstart on Fri Oct 29 13:10:42 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


============================================================
VoxelDesk
============================================================

..
   .. image:: vxd_logo.png



VoxelDesk is a library of Python tools, designed to work with magnetic resonance imaging (MRI) data.
It is aimed at users who provide image processing in a clinical setting.
Some of its key features are listed below:

- Functionality for organizing DICOM files across multiple patients, studies, series, etc.
- DICOM anonymization tools
- Conversion between DICOM and NIFTI file formats
- Streamlined pre-processing of raw diffusion-weighted MRI data, to facilitate tractography.


VoxelDesk utilizes a number of third-party applications and open-source code, which we would like to acknowledge below:

- The `dicomsort <https://github.com/pieper/dicomsort>`_ project
- Chris Roden's `dcm2niix <https://github.com/rordenlab/dcm2niix>`_
- Oxford FMRIB Software Library `FSL <https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FSL>`_
- `MRtrix3 <https://www.mrtrix.org/>`_
- The `pydicom <https://pydicom.github.io/>`_ python tools
- The `deid <https://pydicom.github.io/deid/>`_ anonymization tools

.. warning::

   VoxelDesk software is **not** classified as a medical device, and is issued with no guarantees or warranty.
   It is intended for research purposes only.


Table of Contents
-----------------

.. toctree::
   :maxdepth: 1
   :caption: Installation

   Installing the dependencies <installation/dependencies>
   Installing voxelDesk <installation/vxd>
   Creating the conda virtual environment <installation/conda>
   Setting the environment variables and file permissions <installation/envs>

.. toctree::
   :maxdepth: 1
   :caption: Configuration

   Setting the configuration parameters <setup/config>

.. toctree::
   :maxdepth: 1
   :caption: DICOM Sorting and NIFTI Conversion

   vxdSort.py <vxdSort/vxdSort>

.. toctree::
   :maxdepth: 1
   :caption: DICOM Tools

   vxd_make_dicom.py <vxdDicom/vxd_make_dicom>
   vxd_summarize_dcminfo.py <vxdDicom/vxd_summarize_dcminfo>

.. toctree::
   :maxdepth: 1
   :caption: NIFTI Tools

   vxd_make_nii_rgb.py <vxdNifti/vxd_make_nii_rgb>
   vxd_make_nii_rgb_fusion.py <vxdNifti/vxd_make_nii_rgb_fusion>
   vxd_tidy.py <vxdNifti/vxd_tidy>

.. toctree::
   :maxdepth: 1
   :caption: Diffusion Pre-Processing

   vxd_diff_preproc.py <vxdDiff/vxd_diff_preproc>













