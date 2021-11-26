============================================================
vxd_diff_preproc.py
============================================================

Synopsis
------------
Perform pre-processing steps on raw diffusion-weighted MRI data, prior to performing tractography, using mrtrix3.
**vxd_diff_preproc.py** will perform the following pre-processing steps, all of which use mrtrix3 functions:

- denoising (using `dwidenoise <https://mrtrix.readthedocs.io/en/latest/reference/commands/dwidenoise.html?highlight=dwidenoise>`_)
- remove Gibbs ringing (using `mrdegibbs <https://mrtrix.readthedocs.io/en/latest/reference/commands/mrdegibbs.html?highlight=mrdegibbs>`_ )
- eddy and topup (using `dwifslpreproc <https://mrtrix.readthedocs.io/en/latest/reference/commands/dwifslpreproc.html?highlight=dwifslpreproc>`_)
- brain masking (using `dwi2mask <https://mrtrix.readthedocs.io/en/latest/reference/commands/dwi2mask.html?highlight=dwi2mask>`_)
- DTI calculations (using `dwi2tensor <https://mrtrix.readthedocs.io/en/latest/reference/commands/dwi2tensor.html?highlight=dwi2tensor>`_)
- CSD pre-processing (using `dwi2response <https://mrtrix.readthedocs.io/en/latest/reference/commands/dwi2response.html?highlight=dwi2response>`_ and
  `dwi2fod <https://mrtrix.readthedocs.io/en/latest/reference/commands/dwi2fod.html?highlight=dwi2fod>`_)
- whole-brain tractography (using `tckgen <https://mrtrix.readthedocs.io/en/latest/reference/commands/tckgen.html?highlight=tckgen>`_ and
  `tckmap <https://mrtrix.readthedocs.io/en/latest/reference/commands/tckmap.html?highlight=tckmap>`_)

.. warning::

    **mrtrix3** and **FSL** must be installed prior to running **vxd_diff_preproc.py**


Usage
--------
.. code-block:: text

    vxd_diff_preproc.py -i/--input <Input raw data (DICOM folder or NIFTI file)> [options]

- **-i** / **\--input** *Raw diffusion data*: Pass either a single source NIFTI file (containing the b0 and
  diffusion-weighted volumes), or the parent folder containing the raw DICOM files.

  If a NIFTI file is passed, **vxd_diff_preproc.py** will search for accompanying *.json*, *.bvecs*, and *.vals* files
  with the same base-name, in the same folder, in order to obtain the information needed for pre-processing. These files will have been
  written automatically if the input NIFTI file was created using :ref:`vxdSort`.

  If a DICOM folder is passed instead, the relevant information needed for pre-processing will be read from the DICOM headers.
  This method is recommended if the raw DICOM files are available.

Description
-------------
**vxd_diff_preproc.py** is designed to automate the steps commonly used in the pre-processing of raw diffusion-MRI data.
Some of the steps can be turned on or off using the flags described below.

**vxd_diff_preproc.py** will determine if multi-shell diffusion data has been supplied (i.e. more then one level of diffusion
weighting, or b-value, has been applied). If multi-shell data is available, the **dhollander** method will be used with
`dwi2response <https://mrtrix.readthedocs.io/en/latest/reference/commands/dwi2response.html?highlight=dwi2response>`_ to calculate
the single-fibre response function. If not, then the **tournier** method will be used.

Similarly, if multi-shell diffusion-data has been supplied, the **multi-shell, multi-tissue** method will be used with
`dwi2fod <https://mrtrix.readthedocs.io/en/latest/reference/commands/dwi2fod.html?highlight=dwi2fod>`_, to calculate the
CSD FODs. If single-shell data has been supplied, the **single-shell single-tissue method** will be use (labelled **csd**
in mrtrix3).


.. warning::

    The results from the each of the pre-processing steps should be checked prior to performing tractography.
    Please see the instructions issued in the terminal window during the running of **vxd_diff_preproc.py** for advice on how
    to check different stages of the output.


Options
---------

- **-f** / **\--b0flip** *NIFTI file or DICOM folder*:
  Option to provide a NIFTI file or DICOM folder containing a b0 acquisition with the phase-encoding direction flipped
  by 180 degrees (compared to the raw data). If this is not supplied, the *topup* step will *not* be run as part of the pre-processing.

  |
- **-m** / **\--mask** *NIFTI file or MIF file*:
  Option to provide a NIFTI or MIF (mrtrix3 format) file containing a user-defined mask, within which the diffusion processing will be performed.
  This will over-ride the automated brain-masking pre-processing step, and can be useful for non-brain data, or if the automated brain masking
  is not performing well.

  |
- **-p** / **\--pedir** *Phase-encoding direction*:
  Option to specify which direction the phase-encoding was applied in, in the raw data. **vxd_diff_preproc.py** will search
  either the JSON sidecar file (for NIFTI data), or the DICOM header (for DICOM data) to extract this information, so this
  option is only necessary if neither of these are available, and the *topup* pre-processing step is requested.

  The specified phase-encoding direction must be one of the following:
  [-0, +0, -1, +1, -2, +2, lr, rl, pa, ap, is, si, i-, i+, j-, j+, k-, k+].

  |
- **-xe** / **\--noeddy**:
  Flag to skip the eddy-correct pre-processing step.

  |
- **-xt** / **\--notract**:
  Flag to skip the whole-brain tractography step.


Example Usages
----------------
- Perform pre-processing on the raw diffusion-MRI DICOM data stored in */path/to/dicom/folder/*. Additionally supply a
  b0 DICOM dataset, with the PE direction flipped by 180 degrees, to allow *topup* to run.

  .. code-block:: text

    vxd_diff_preproc.py -i /path/to/rawdata/dicom/folder/ -f path/to/b0flip/dicom/folder

  The raw data and b0flip data will be converted into the mrtrix3 *.mif* file format. The relevant information needed for
  pre-processing (diffusion b-values, diffusion gradient directions, phase-encoding direction) will be automatically read
  from the DICOM headers and stored in the *.mif* header.

  |
- Perform pre-processing on the raw diffusion-MRI data stored in dwi_raw.nii.gz. This is a NIFTI file which was previously
  converted from DICOM format using :ref:`vxdSort`.

  .. code-block:: text

    vxd_diff_preproc.py -i dwi_raw.nii.gz

  Because the NIFTI conversion was performed using :ref:`vxdSort`, accompanying *dwi_raw.json*, *dwi_raw.bval*, and *dwi_raw.bvec* files
  also exist in the same folder as *dwi_raw.nii.gz*. **vxd_diff_preproc.py** will read the information stored in these files, and
  combine it with the raw data in dwi_raw.nii.gz, to create a new .mif file.

  <<<TEST>>>

  Because no b0flip file was supplied, *topup* will not be run.