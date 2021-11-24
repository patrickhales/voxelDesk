============================================================
vxd_summarize_dcminfo.py
============================================================

Synopsis
------------
Output a text file summarizing the information stored in the DICOM header of a given DICOM file.

Usage
--------
.. code-block:: text

    vxd_summarize_dcminfo.py -i/--input path/to/dicomfile [options]


Description
-------------
By default, **vxd_summarize_dcminfo.py** will output a text file summarizing the key DICOM tags defined in the following file
``$VXD_HOME/VxdDicom/key_dicom_tags.txt``. Each tag is written to a new line, with tag names are their associated values
separated using a colon.

A default set of key dicom tags are provided in the ``$VXD_HOME/VxdDicom/key_dicom_tags.txt``. This list can be edited by
the user, to focus on the DICOM tags which are most relevant (note the default set are quite Siemens orientated!).

The additional information stored in the Siemens CSA DICOM Header is also read, and any information stored here which is
listed in the *key_dicom_tags.txt* files will be written out.

In addition, the full DICOM header (including the Siemens CSA information) can be written to the text file, using the **-f / \--full** option (see below).

The resulting text files will have the same name as the *SeriesDesciption* DICOM tag, appended with *_dcminfo_key.txt* (for the
key DICOM tags) and *_dcminfo.txt* (for the full DICOM header info, if requested).


Options
---------

- **-f** / **\--full**: output an additional text file, containing the full DICOM header.

Example Usages
----------------

- Write a summary text file with the key DICOM tags, as well as a more detailed text file with the complete DICOM header

.. code-block:: text

    vxd_summarize_dcminfo.py --input path/to/dicomfile --full




