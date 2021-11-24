.. _config:

===============================================================
Setting the Configuration Parameters
===============================================================

The global parameter settings for voxelDesk are stored in the ``config.json`` file, which resides in the ``$VXD_HOME/vxdSetup`` folder.

The voxelDesk installation comes with a default  ``config.json`` file.
To make changes to any of the default parameter settings, first open the ``$VXD_HOME/writeConfigFile.py`` python script,
in your favourite editor.

All configuration parameters are held in a Python dictionary called ``config``, entries from which are written to the ``config.json`` file.
Values for different keys in the dictionary can be set by editing the entries in the ``$VXD_HOME/writeConfigFile.py`` python script.

Following this, the ``config.json`` file must be updated. This can be done by running the **writeConfigFile** function from a terminal window, i.e.

::

    writeConfigFile.py

An explanation of the keys used in the ``config`` dictionary is given below:

- ``config['sortedDicomFolderName']`` = folder name used to store sorted DICOM files (default: ``vxd_dicom``)
- ``config['sortedNiftiFolderName']`` = folder name used to store sorted NIFTI files (default: ``vxd_nifti``)
- ``config['defaultTargetPattern']`` = string defining the output file and directory names based on the DICOM tags in the file. The default is:

::

    /%PatientName/%StudyDate/%SeriesNumber-%SeriesDescription/%SeriesDescription-%InstanceNumber.dcm'

which will tell voxelDesk to sort DICOM files into the following file structure:

.. code-block:: text

    - PatientName
    --- 20211110 <study date in yyyymmdd format>
    ------ 001-t2_tse_tra_2mm <series number-series description>
    --------- t2_tse_tra_2mm-001.dcm <series description-instance number>
    --------- t2_tse_tra_2mm-002.dcm etc...


-  ``config['excludeNifti']`` = list of series descriptions to skip in the conversion between DICOM and NIFTI. Some DICOM series,
    such as 3-plane localizers and diffusion tensor DICOM files, do not convert reliably to NIFTI format
    (default ``['localizer', 'survey', 'phoenix', 'iso_tensor']``)


-   ``config['deidRecipe']`` = The name of the deid receipe file used to anonymize DICOMs (default: ``deid_voxelDesk.dicom``).
    This file must reside in the ``$VXD_HOME/vxdSort`` folder. If you would like to customize the anonymization procedure,
    information on how to use *deid* recipe files can be found `here <https://pydicom.github.io/deid/examples/recipe/>`_.



.. warning::

   The anonymization provided by voxelDesk software is issued with no guarantees or warranty.
   Always check the anonymization requirements of your local ethics committee or IRB.







