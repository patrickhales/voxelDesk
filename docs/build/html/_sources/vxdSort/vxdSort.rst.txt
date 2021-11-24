.. _vxdSort:

===========
vxdSort.py
===========

Synopsis
------------
Sort DICOM files into patient/study/series hierarchy, and convert to NIFTI. This module also provides anonymization
options for the sorted DICOM files.

Usage
--------

.. code-block:: text

    vxdSort.py -i/--input <source DICOM folder> [options]


- Use either **-i** or **\--input** to specify the path to the source folder, containing the DICOM files


Description
-------------
If no additional options are passed, this program will sort all DICOM files present in the *source DICOM folder* into a hierarchical structure.

The output is written to a new subfolder, within the *source DICOM folder* root. The name of the output folder is specified
in the **config.json** file (see  :ref:`config`; the default is **vxd_dicom**). By default, the output follows the format shown below.
If multiple patients are present in the source DICOM folder, a new patient folder will be created for each.

::

    - patient name
    --- study date <yyyymmdd>
    ------ series 01
    ------ series 02, etc...

Options
---------

- **-n** / **\--nifti**
  Flag to create a mirrored copy of the sorted DICOM files, in NIFTI format.
  A new parent folder will be created (default folder name is **vxd_nifti**). The file structure within this will match that used for the sorted DICOM files,
  with a compressed NIFTI file being stored in each series subfolder. Series with a *SeriesDesciption* DICOM tag listed in the
  **config['excludeNifti']** dictionary entry will not be converted to NIFTI (see  :ref:`config`).
  An additional JSON *sidecar* file will be written, containing a summary of some key DICOM tags.

  |
- **-a** / **\--anon**
  Flag to anonymize the DICOM files as they are sorted. The recipe file stored in **$VXD_HOME/vxdSort/deid_voxelDesk.dicom**
  will be used to determine which DICOM tags should be removed or updated. This recipe file can be edited - see :ref:`config`).

  By default, the patient names in the *source DICOM folder* will be replaced by **vxdAnon-0000**, **vxdAnon-0001**, etc, however,
  this can be changed using the **\--codes** option described below.

  |
- **-c** / **\--codes** 'list of patient codes'.
  Replaces the *PatientName* and *PatientID* DICOM tags in the anonymized files with a user-supplied patient code.
  Supply one code for each patient present in the *source DICOM folder*, using a comma-separated list.

Example Usages
----------------

- Sort the DICOM files stored in the *myDICOMs* folder into patient/study/series folders:

  .. code-block:: text

    vxdSort.py --input myDICOMs

  This will create a new folder called *myDICOMs/vxd_dicom*, containing the sorted DICOM files.

  |
- Sort the DICOM files stored in the *myDICOMs* folder, and create NIFTI versions of each series

  .. code-block:: text

    vxdSort.py --input myDICOMs --nifti

  This will create two new folders: *myDICOMs/vxd_dicom* for the sorted DICOMS, and *myDICOMs/vxd_nifti* for the NIFTIs.

  |
- Sort the DICOM files stored in the *myDICOMs* folder, and anonymize the sorted files

  .. code-block:: text

    vxdSort.py --input myDICOMs --anon

  This will create a new folder called *myDICOMs/vxd_dicom*, containing the sorted DICOM files. As the **\--codes**
  option has not been used, each patient in the *myDICOMs* folder will be renamed as *vxdAnon-0000*, *vxdAnon-0001*, etc.

  |
- Sort the DICOM files stored in the *myDICOMs* folder, anonymize the sorted files with user-supplied patient codes,
  and convert to NIFTI

  .. code-block:: text

    vxdSort.py --input <source DICOM folder> --anon --codes 'Patient-001, Patient-002' --nifti

  This will create two new folders: *myDICOMs/vxd_dicom* for the sorted DICOMS, and *myDICOMs/vxd_nifti* for the NIFTIs.
  The patient folders will be named *myDICOMs/vxd_dicom/Patient-001* and *myDICOMs/vxd_dicom/Patient-002*.


